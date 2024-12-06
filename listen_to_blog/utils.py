import frappe
from elevenlabs.client import ElevenLabs


def get_elevenlabs_client():
	api_key = frappe.get_cached_doc("ElevenLabs Settings").get_password("api_key")

	return ElevenLabs(api_key=api_key)

