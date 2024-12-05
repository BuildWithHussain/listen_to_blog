// Copyright (c) 2024, BWH and contributors
// For license information, please see license.txt

frappe.ui.form.on("ElevenLabs Settings", {
	refresh(frm) {
		frm.add_custom_button("Generate Missing Audio Files", () => {
			frappe.call("listen_to_blog.utils.generate_missing_audio_files").then(() => {
				frappe.show_alert({
					message: "Successfully generated!",
					indicator: "green"
				})
			})
		})
	},
});
