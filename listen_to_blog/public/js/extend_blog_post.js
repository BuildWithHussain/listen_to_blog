frappe.ui.form.on("Blog Post", {
	refresh(frm) {
		const buttonLabel = frm.doc.custom_audio ? "Regenerate Audio"  : "Generate Audio";
		frm.add_custom_button(buttonLabel, () => {
			frappe.call({
				method: "listen_to_blog.audio_generator._generate_and_attach_audio_file",
				args: {
					blog_post_doc: frm.doc
				}
			}).then(() =>  {
				frappe.show_alert("Generation complete.")
				frm.reload_doc();
			})
		})
	}
})
