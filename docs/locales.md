# Interaction models and free-text answers

Import the complete JSON model for the device/test locale, then Save and Build it in the Alexa developer console. Models and manifest entries now include `en-CA`, `en-IN`, and `es-US` as well as the original `en-US`, `en-GB`, `de-DE`, `fr-FR`, `it-IT`, `pt-BR`, and `es-ES`. A new region uses the existing language's model/prompts as a starting point; pronunciation and utterance recognition still need regional tester feedback. Importing only custom intents omits the built-in Yes/No/Fallback routing.

Each model declares Yes, No, Cancel, Stop, Help and Fallback. Numbers use `AMAZON.NUMBER`, rather than restricting the UK model to four digits. The French prompt override is `fr-FR` (correcting `ft-FR`). Unknown/missing backend locales fall back to English instead of throwing a lookup error. This fallback does not advertise a new locale or create a model for it.

The new **FreeText** intent uses `AMAZON.SearchQuery` and emits the same `ResponseString` event as the older String intent. Amazon requires a carrier phrase in intent samples; a bare `{FreeTextValue}` sample is not supported. Say:

| Language | Example |
| --- | --- |
| English | my answer is leave the kitchen lights on |
| German | meine Antwort ist lass das Licht an |
| Spanish | mi respuesta es deja la luz encendida |
| French | ma réponse est laisse la lumière allumée |
| Italian | la mia risposta è lascia la luce accesa |
| Portuguese | minha resposta é deixe a luz acesa |

The existing String/person-name intent remains for backward compatibility. Yes/No, numbers, selections, dates and durations retain their existing names and response types. A carrier phrase keeps broad free text from competing directly with short Yes/No answers. This is speech recognition through Amazon's phrase slot, not access to a raw microphone transcript or guaranteed arbitrary dictation.

`es-US` includes explicit No samples (`no`, `no gracias`, `claro que no`). This provides the missing locale/model path; whether a particular utterance is recognized on a physical device must be checked in the console's utterance profiler/simulator and by Spanish-US device owners. Italian/Canadian/Indian reflector or fallback reports should first check that the correct full regional model was built and that the backend received the intended intent name.

Use [Alexa's model/testing tools](https://developer.amazon.com/en-US/docs/alexa/custom-skills/test-and-debug-a-custom-skill.html) and [simulator](https://developer.amazon.com/en-US/docs/alexa/devconsole/alexa-simulator.html) without an Echo. Offline tests check model/manifest agreement, handler/slot contracts and real SDK dispatch, but cannot replace Amazon's server-side model build or recognition tests. No model build in a personal Amazon account or live device test is claimed here.

Based on current [SearchQuery support and carrier rules](https://developer.amazon.com/en-US/docs/alexa/custom-skills/slot-type-reference.html#amazonsearchquery), [built-in intents](https://developer.amazon.com/en-US/docs/alexa/custom-skills/standard-built-in-intents.html) and [multilingual skill guidance](https://developer.amazon.com/en-US/docs/alexa/custom-skills/develop-skills-in-multiple-languages.html), checked 2026-09-26.
