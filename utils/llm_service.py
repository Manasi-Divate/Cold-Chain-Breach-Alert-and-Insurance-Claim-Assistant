import os

try:
    import openai
except ImportError:  # pragma: no cover
    openai = None

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')


def llm_available(api_key=None):
    key = api_key or OPENAI_API_KEY
    return openai is not None and key is not None


def _initialize_openai(api_key=None):
    if openai is not None:
        key = api_key or OPENAI_API_KEY
        if key:
            openai.api_key = key


def _create_prompt(excursion, report_type):
    if report_type == 'fda':
        return (
            'Generate a concise FDA/WHO-style cold-chain breach report using the following data. '
            'Include bag ID, start and end times, duration, max temperature, severity, impact, and recommended action.\n\n'
            f'Bag ID: {excursion["bag_id"]}\n'
            f'Start Time: {excursion["start_time"]}\n'
            f'End Time: {excursion["end_time"]}\n'
            f'Duration: {excursion["duration_minutes"]} minutes\n'
            f'Max Temperature: {excursion["max_temperature"]} °C\n'
            f'Severity: {excursion["severity"]}\n'
        )
    return (
        'Generate a concise insurance claim request for a cold-chain temperature breach. '
        'Use the following data and include claim status, reason for claim, and recommended next steps.\n\n'
        f'Bag ID: {excursion["bag_id"]}\n'
        f'Start Time: {excursion["start_time"]}\n'
        f'End Time: {excursion["end_time"]}\n'
        f'Duration: {excursion["duration_minutes"]} minutes\n'
        f'Max Temperature: {excursion["max_temperature"]} °C\n'
        f'Severity: {excursion["severity"]}\n'
    )


def _call_openai(prompt, api_key=None):
    _initialize_openai(api_key)
    try:
        response = openai.ChatCompletion.create(
            model='gpt-3.5-turbo',
            messages=[
                {'role': 'system', 'content': 'You are a helpful assistant that writes compliance reports and insurance claims.'},
                {'role': 'user', 'content': prompt},
            ],
            max_tokens=400,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as exc:
        return f'LLM generation failed: {exc}'


def generate_llm_fda_report(excursion, api_key=None):
    if not llm_available(api_key):
        return ''
    prompt = _create_prompt(excursion, 'fda')
    return _call_openai(prompt, api_key)


def generate_llm_insurance_claim(excursion, api_key=None):
    if not llm_available(api_key):
        return ''
    prompt = _create_prompt(excursion, 'insurance')
    return _call_openai(prompt, api_key)
