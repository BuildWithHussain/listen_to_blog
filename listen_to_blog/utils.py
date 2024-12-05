import frappe
from elevenlabs.client import ElevenLabs


def generate_audio_file_for_blog_post(doc, event=None):
	if not has_content_changed(doc):
		return

	# generate the audio
	if not frappe.conf.developer_mode:
		frappe.enqueue(
			"listen_to_blog.utils._generate_and_attach_audio_file",
			queue="long",
			enqueue_after_commit=True,
			blog_post=doc,
		)
	else:
		_generate_and_attach_audio_file(doc)


TYPE_CONTENT_FIELD_MAP = {"Markdown": "content_md", "HTML": "content_html", "Rich Text": "content"}


def has_content_changed(doc):
	content_field = TYPE_CONTENT_FIELD_MAP[doc.content_type]
	return doc.has_value_changed(content_field)


def _generate_and_attach_audio_file(blog_post):
	client = get_elevenlabs_client()
	voice_id = "iP95p4xoKVk53GoZ742B"

	content_field = TYPE_CONTENT_FIELD_MAP[blog_post.content_type]
	text = blog_post.get(content_field)

	audio = client.generate(text=text, voice=voice_id, model="eleven_multilingual_v2")

	create_file_doc(blog_post, audio)


def get_elevenlabs_client():
	api_key = frappe.get_cached_doc("ElevenLabs Settings").get_password("api_key")

	return ElevenLabs(api_key=api_key)


def create_file_doc(blog_post, audio):
	delete_old_file_if_exists(blog_post)

	import io

	output = io.BytesIO()
	for chunk in audio:
		if chunk:
			output.write(chunk)
	file_data = output.getvalue()

	file = frappe.get_doc(
		{
			"doctype": "File",
			"file_name": f"{blog_post.name}.mp3",
			"content": file_data,
			"attached_to_doctype": "Blog Post",
			"attached_to_name": blog_post.name,
			"attached_to_field": "custom_audio"
		}
	).save()

	blog_post.db_set("custom_audio", file.file_url)


def delete_old_file_if_exists(blog_post):
	file_name =  f"{blog_post.name}.mp3"
	exists = frappe.db.exists("File", {"file_name": file_name})

	if exists:
		frappe.get_doc("File", {"file_name": file_name}).delete()
