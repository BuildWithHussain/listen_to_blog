import frappe

from listen_to_blog.utils import get_elevenlabs_client

TYPE_CONTENT_FIELD_MAP = {"Markdown": "content_md", "HTML": "content_html", "Rich Text": "content"}


class BlogPostAudioGenerator:
	def __init__(self, blog_post: str, content: str) -> None:
		self.blog_post = blog_post
		self.content = content

	def generate(self) -> None:
		client = get_elevenlabs_client()
		voice_id = "iP95p4xoKVk53GoZ742B"

		text = self.content

		audio = client.generate(text=text, voice=voice_id, model="eleven_multilingual_v2")
		self.create_file(audio)

	def create_file(self, audio) -> None:
		self.delete_old_file_if_exists()

		import io

		output = io.BytesIO()
		for chunk in audio:
			if chunk:
				output.write(chunk)
		file_data = output.getvalue()

		file = frappe.get_doc(
			{
				"doctype": "File",
				"file_name": f"{self.blog_post}.mp3",
				"content": file_data,
				"attached_to_doctype": "Blog Post",
				"attached_to_name": self.blog_post,
				"attached_to_field": "custom_audio",
			}
		).save()

		frappe.db.set_value("Blog Post", self.blog_post, "custom_audio", file.file_url)

	def delete_old_file_if_exists(self) -> None:
		file_name = f"{self.blog_post}.mp3"
		exists = frappe.db.exists("File", {"file_name": file_name})

		if exists:
			frappe.get_doc("File", {"file_name": file_name}).delete()

@frappe.whitelist()
def _generate_and_attach_audio_file(blog_post_doc):
	if isinstance(blog_post_doc, str):
		blog_post_doc = frappe.parse_json(blog_post_doc)

	field_name = TYPE_CONTENT_FIELD_MAP[blog_post_doc.content_type]
	generator = BlogPostAudioGenerator(blog_post_doc.name, blog_post_doc.get(field_name))
	generator.generate()


def has_content_changed(doc):
	content_field = TYPE_CONTENT_FIELD_MAP[doc.content_type]
	return doc.has_value_changed(content_field)


def generate_audio_file_for_blog_post(doc, event=None):
	if not has_content_changed(doc):
		return

	# generate the audio
	if not frappe.conf.developer_mode:
		frappe.enqueue(
			"listen_to_blog.audio_generator._generate_and_attach_audio_file",
			queue="default",
			enqueue_after_commit=True,
			blog_post=doc,
		)
	else:
		_generate_and_attach_audio_file(doc)


def generate_missing_audio_files():
	posts_with_no_audio = frappe.get_all("Blog Post", filters={"custom_audio": ("is", "not set")}, pluck="name")

	for post in posts_with_no_audio:
		_generate_and_attach_audio_file(frappe.get_doc("Blog Post", post))

@frappe.whitelist()
def enqueue_bulk_audio_generation():
	frappe.enqueue(generate_missing_audio_files, queue="long")
