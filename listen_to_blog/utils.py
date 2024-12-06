import frappe
from elevenlabs.client import ElevenLabs


def get_elevenlabs_client():
	api_key = frappe.get_cached_doc("ElevenLabs Settings").get_password("api_key")

	if not api_key:
		frappe.throw("Please set your API Key in ElevenLabs Settings before generating audio!")

	return ElevenLabs(api_key=api_key)

