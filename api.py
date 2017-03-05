from include.friendly_train.main import LanguageGenerator3000
import random
from flask import Flask, render_template, redirect
app = Flask(__name__)


langgen = LanguageGenerator3000()


def get_random_word():
  return random.choice(['random_aus_funktion', 'wurst', 'käse', 'fisch'])


def get_correlated_sentence(word):
  return 'Korrelierter Satz [' + str(random.randint(10, 99)) + '] zum Wort "' + word + '".'


def get_word_type(word):
  return 'verb'


def get_word_list():
  return ['random_aus_funktion', 'wurst', 'käse', 'fisch']


def get_wordcloud(word):
  weights = {'verb': {'random_aus_funktion': {'fisch': 1, 'frosch': 2, 'film': 0.7}, 'wurst': {'fisch': 1, 'frosch': 2, 'film': 0.7},
                      'käse': {'fisch': 1, 'frosch': 2, 'film': 0.7}, 'fisch': {'fisch': 1, 'frosch': 2, 'film': 0.7}}}
  to_normalize = weights[get_word_type(word)][word]
  wordcloud = {}
  cnt = 0
  max_value = None
  min_value = None
  own_word_type = get_word_type(word)
  for key, value in sorted(to_normalize.items(), key=lambda x: x[1], reverse=True):
    cnt += 1
    if key != word and cnt < 20 and get_word_type(key) == own_word_type:
      wordcloud[key] = value
      if max_value is None:
        max_value = value
      if min_value is None:
        min_value = value
      if value < min_value:
        min_value = value

  # normalize
  for word in wordcloud:
    wordcloud[word] -= min_value * 0.4
    wordcloud[word] /= (max_value - min_value) * 1.5
  return wordcloud


# generate static texts
main_title = get_random_word()
sub_title = get_correlated_sentence(main_title)
special_word = get_random_word()
allowed_action_words = []
for i in range(6):
  allowed_action_words.append(get_random_word())

menu_items = {'Menüitem 1': '/' + special_word + '/' + 'anderes_aktionswort',
              'Menüitem 2': '/' + 'normales_wort',
              'Menüitem 3': '/' + 'voll_tolles_wort'}
toc = get_random_word()

colors = ['red', 'pink', 'purple', 'deep-purple', 'indigo', 'blue', 'light-blue', 'cyan', 'teal',
          'green', 'light-green', 'lime', 'yellow', 'amber', 'orange',
          'deep-orange', 'brown', 'grey', 'blue-grey'
          ]
footer_title = 'Titel des footerssss<fdadsf adhBFDSAF'
footer_text = 'Hier steht ein etwas längerer Text im Footer. Einige Sätze zumindest.'
footer_links_heading = 'überschrift für links'
bottom_line_text = 'Text in der Fußzeile'
footer_links = {'Footer link 1': '/' + special_word + '/' + random.choice(allowed_action_words),
                'link2': '/' + 'rdm_wort',
                }

default_context = {
    'title': main_title,
    'sub_title': sub_title,
    'menu_items': menu_items,
    'color': random.choice(colors),
    'footer_title': footer_title,
    'footer_text': footer_text,
    'footer_links_heading': footer_links_heading,
    'bottom_line_text': bottom_line_text,
    'footer_links': footer_links,
    'toc': toc,
    'special_word': special_word,
}

rdm_sentences = []
for i in range(7):
  rdm_sentences.append(get_correlated_sentence(main_title))
description = ' '.join(rdm_sentences)


@app.route('/')
def index():
  return render_template('index.html', vars=default_context, desc=description, action_words=allowed_action_words)


@app.route('/<string:word>')
def detail(word):
  # generate paragraphs
  paragraphs = {}
  random.seed(word)
  for i in range(random.randint(2, 5)):
    sentences = []
    for j in range(random.randint(3, 12)):
      sentences.append(get_correlated_sentence(word))
    text = ' '.join(sentences)
    paragraphs[get_correlated_sentence(word)] = {'text': text, 'index': i}
  return render_template('detail.html', vars=default_context, word=word, article=paragraphs, wordcloud=get_wordcloud(word))


@app.route('/' + special_word + '/<string:action_word>')
def action(action_word):
  # check if is allowed action word?
  if action_word not in allowed_action_words:
    return 'fehler'
  random_word = get_random_word()
  random.seed(special_word + '/' + action_word)
  random_number = random.randint(0, 1)
  if 0 == random_number:
    # random article
    return redirect('/' + random_word)
  if 1 == random_number:
    # full word list
    return render_template('list.html', vars=default_context, word_list=get_word_list())


if __name__ == "__main__":
  app.run(debug=True)
