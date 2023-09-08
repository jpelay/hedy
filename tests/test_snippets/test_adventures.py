import os
from app import translate_error, app
from flask_babel import force_locale

from parameterized import parameterized

import exceptions
import hedy
import utils
from tests.Tester import HedyTester, Snippet
from website.yaml_file import YamlFile

# Set the current directory to the root Hedy folder
os.chdir(os.path.join(os.getcwd(), __file__.replace(os.path.basename(__file__), '')))

filtered_language = None
level = None


def collect_snippets(path, filtered_language=None):
    Hedy_snippets = []
    files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f)) and f.endswith('.yaml')]
    for f in files:
        lang = f.split(".")[0]
        if not filtered_language or (filtered_language and lang == filtered_language):
            f = os.path.join(path, f)
            yaml = YamlFile.for_file(f)

            for name, adventure in yaml['adventures'].items():
                # the default tab sometimes contains broken code to make a point to learners about changing syntax.
                if not name == 'default':
                    for level_number in adventure['levels']:
                        if level_number > hedy.HEDY_MAX_LEVEL:
                            print('content above max level!')
                        else:
                            level = adventure['levels'][level_number]
                            adventure_name = adventure['name']

                            code_snippet_counter = 0
                            # code snippets inside story_text
                            for tag in utils.markdown_to_html_tags(level['story_text']):
                                if tag.name != 'pre' or not tag.contents[0]:
                                    continue
                                # Can be used to catch more languages with example codes in the story_text
                                # feedback = f"Example code in story text {lang}, {adventure_name},
                                # {level_number}, not recommended!"
                                # print(feedback)
                                code_snippet_counter += 1
                                try:
                                    code = tag.contents[0].contents[0]
                                except BaseException:
                                    print("Code container is empty...")
                                    continue

                                snippet = Snippet(
                                    filename=f,
                                    level=level_number,
                                    field_name=adventure_name + ' snippet #' + str(code_snippet_counter),
                                    code=code,
                                    adventure_name=adventure_name)
                                Hedy_snippets.append(snippet)

                            # code snippets inside start_code
                            try:
                                start_code = level['start_code']
                                snippet = Snippet(
                                    filename=f,
                                    level=level_number,
                                    field_name='start_code',
                                    code=start_code,
                                    adventure_name=adventure_name)
                                Hedy_snippets.append(snippet)

                            except KeyError:
                                print(f'Problem reading startcode for {lang} level {level}')
                                pass
                            # Code snippets inside example code
                            try:
                                example_code = utils.markdown_to_html_tags(level['example_code'])
                                for tag in example_code:
                                    if tag.name != 'pre' or not tag.contents[0]:
                                        continue
                                    code_snippet_counter += 1
                                    try:
                                        code = tag.contents[0].contents[0]
                                    except BaseException:
                                        print("Code container is empty...")
                                        continue

                                    snippet = Snippet(
                                        filename=f,
                                        level=level_number,
                                        field_name=adventure_name + ' snippet #' + str(code_snippet_counter),
                                        code=code,
                                        adventure_name=adventure_name)
                                    Hedy_snippets.append(snippet)
                            except Exception as E:
                                print(E)

    return Hedy_snippets

# filtered_language = 'fr'
# use this to filter on 1 lang, zh_Hans for Chinese, nb_NO for Norwegian, pt_PT for Portuguese


Hedy_snippets = [(s.name, s) for s in collect_snippets(path='../../content/adventures',
                                                       filtered_language=filtered_language)]

# level = 5
# if level:
#     Hedy_snippets = [(name, snippet) for (name, snippet) in Hedy_snippets if snippet.level == level]

# This allows filtering out languages locally, but will throw an error
# on GitHub Actions (or other CI system) so nobody accidentally commits this.
if os.getenv('CI') and (filtered_language or level):
    raise RuntimeError('Whoops, it looks like you left a snippet filter in!')

Hedy_snippets = HedyTester.translate_keywords_in_snippets(Hedy_snippets)


class TestsAdventurePrograms(HedyTester):

    @parameterized.expand(Hedy_snippets, skip_on_empty=True)
    def test_adventures(self, name, snippet):
        if snippet is not None and len(snippet.code) > 0:
            try:
                self.single_level_tester(
                    code=snippet.code,
                    level=int(snippet.level),
                    lang=snippet.language,
                    translate=False
                )

            except hedy.exceptions.CodePlaceholdersPresentException:  # Code with blanks is allowed
                pass
            except OSError:
                return None  # programs with ask cannot be tested with output :(
            except exceptions.HedyException as E:
                try:
                    location = E.error_location
                except BaseException:
                    location = 'No Location Found'

                # Must run this in the context of the Flask app, because FlaskBabel requires that.
                with app.app_context():
                    with force_locale('en'):
                        error_message = translate_error(E.error_code, E.arguments, 'en')
                        error_message = error_message.replace('<span class="command-highlighted">', '`')
                        error_message = error_message.replace('</span>', '`')
                        print(f'\n----\n{snippet.code}\n----')
                        print(f'from adventure {snippet.adventure_name}')
                        print(f'in language {snippet.language} from level {snippet.level} gives error:')
                        print(f'{error_message} at line {location}')
                        raise E
