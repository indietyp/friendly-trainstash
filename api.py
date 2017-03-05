from include.friendly_train.main import LanguageGenerator3000
import random
from flask import Flask, render_template, redirect
app = Flask(__name__)


random.seed(213)


langgen = LanguageGenerator3000()
cached_list = None


def get_word_list():
  global cached_list
  if cached_list is None:
    cached_list = []
    for word in langgen.generate_word_list():
      cached_list.append(word['word'])
  return cached_list


def is_word(word):
  return word in cached_list


def get_random_word():
  return random.choice(get_word_list())


def get_correlated_sentences(word, count=1):
  word_object = {'word': word, 'type': get_word_type(word)}
  received_sentences = langgen.generate_sentence_list(sample_size=count, random_sentence_structure=True, correlation=word_object)
  answer = []
  for single_sentence_object in received_sentences:
    answer.append(single_sentence_object['sentence'].capitalize())
  return answer


def get_correlated_sentence(word):
  return get_correlated_sentences(word, count=1).pop()


def get_word_type(word):
  return langgen.get_word_type(word)


def get_wordcloud(word):
  weights = langgen.get_weights()
  to_normalize = weights[get_word_type(word)][word]
  wordcloud = {}
  cnt = 0
  max_value = None
  min_value = None
  own_word_type = get_word_type(word)
  for key, value in sorted(to_normalize.items(), key=lambda x: x[1], reverse=True):
    if key != word and cnt < 20 and get_word_type(key) == own_word_type:
      cnt += 1
      wordcloud[key] = value
      if max_value is None:
        max_value = value
      if min_value is None:
        min_value = value
      if value < min_value:
        min_value = value

  # normalize
  for word in wordcloud:
    wordcloud[word] -= min_value * 0.8
    wordcloud[word] /= (max_value - min_value)
  return wordcloud


# generate static texts
main_title = get_random_word()
sub_title = get_correlated_sentence(main_title)
special_word = get_random_word()
allowed_action_words = []
for i in range(6):
  allowed_action_words.append(get_random_word())

menu_items = {}
for i in range(random.randint(2, 3)):
  if 0 == random.randint(0, 1):
    # pick special word
    action_word = random.choice(allowed_action_words)
    menu_items[action_word] = '/' + special_word + '/' + action_word
  else:
    # pick normal article
    rdm_word = get_random_word()
    menu_items[rdm_word] = '/' + rdm_word

colors = ['red', 'pink', 'purple', 'deep-purple', 'indigo', 'blue', 'light-blue', 'cyan', 'teal',
          'green', 'light-green', 'lime', 'yellow', 'amber', 'orange',
          'deep-orange', 'brown', 'grey', 'blue-grey'
          ]
footer_title = get_random_word()
footer_text = ' '.join(get_correlated_sentences(footer_title, count=5))
footer_links_heading = get_correlated_sentence(footer_title)
bottom_line_text = get_correlated_sentence(main_title)
footer_links = {}
for i in range(random.randint(2, 3)):
  if 0 == random.randint(0, 1):
    # pick special word
    action_word = random.choice(allowed_action_words)
    footer_links[action_word] = '/' + special_word + '/' + action_word
  else:
    # pick normal article
    rdm_word = get_random_word()
    footer_links[rdm_word] = '/' + rdm_word

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
  if not is_word(word):
    return redirect('/')
  # generate paragraphs
  paragraphs = {}
  random.seed(word)
  to_linkify = []
  for i in range(random.randint(2, 5)):
    sentences = []
    word_object = {'word': word, 'type': get_word_type(word)}
    received_sentence_list = langgen.generate_sentence_list(sample_size=random.randint(3, 12), random_sentence_structure=True, correlation=word_object)
    for single_sentence_object in received_sentence_list:
      sentences.append(single_sentence_object['sentence'].capitalize())
      for single_word_object in single_sentence_object['raw']['text']:
        if random.randint(1, 42) < 3:
          to_linkify.append(single_word_object['word'])
          to_linkify.append(single_word_object['word'].capitalize())
    text = ' '.join(sentences)
    paragraphs[get_correlated_sentence(word)] = {'text': text, 'index': i}
  return render_template('detail.html', vars=default_context, word=word, article=paragraphs, wordcloud=get_wordcloud(word), to_linkify=to_linkify)


@app.route('/' + special_word + '/<string:action_word>')
def action(action_word):
  # check if is allowed action word?
  if action_word not in allowed_action_words:
    return redirect('/')
  random_word = get_random_word()
  random.seed(special_word + '/' + action_word)
  random_number = random.randint(0, 1)
  if 0 == random_number:
    # random article
    return redirect('/' + random_word)
  if 1 == random_number:
    # full word list
    return render_template('list.html', vars=default_context, word_list=get_word_list())


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
  return redirect('/')


if __name__ == "__main__":
  app.run()
