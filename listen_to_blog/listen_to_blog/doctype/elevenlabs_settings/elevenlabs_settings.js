// Copyright (c) 2024, BWH and contributors
// For license information, please see license.txt

frappe.ui.form.on("ElevenLabs Settings", {
	refresh(frm) {
		frm.add_custom_button("Generate Missing Audio Files", () => {
			frappe.call("listen_to_blog.audio_generator.enqueue_bulk_audio_generation").then(() => {
				frappe.show_alert({
					message: "Successfully queued generation of audio files!",
					indicator: "green"
				})
			})
		})
	},
});
