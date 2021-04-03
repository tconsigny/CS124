# PA6, CS124, Stanford, Winter 2019
# v.1.0.3
# Original Python code by Ignacio Cases (@cases)
######################################################################
import movielens
import numpy as np
import re
import collections
from nltk.stem import PorterStemmer
from nltk.tokenize import sent_tokenize, word_tokenize
import random


class Chatbot:
    """Simple class to implement the chatbot for PA 6."""

    def __init__(self, creative=False):
      # The chatbot's default name is `moviebot`. Give your chatbot a new name.
      self.name = 'MotherBot'

      self.creative = creative

      # This matrix has the following shape: num_movies x num_users
      # The values stored in each row i and column j is the rating for
      # movie i by user j
      self.titles, ratings = movielens.ratings()
      self.sentiment = movielens.sentiment()

      #############################################################################
      # TODO: Binarize the movie ratings matrix.                                  #
      #############################################################################

      # Binarize the movie ratings before storing the binarized matrix.
      self.ratings = self.binarize(ratings)
      assert(len(self.titles) == len(self.ratings))
      self.user_ratings = np.zeros((len(self.titles),))

      self.n_data_points = 0
      self.casual_titles = self.make_casual_titles() if self.creative else []

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################

    #############################################################################
    # 1. WARM UP REPL                                                           #
    #############################################################################


    def make_casual_titles(self):
      casual_titles = []

      for t in self.titles:
        t = t[0]
        title, year = self.titleAndYear(t)
        titles = self.allTitleOpts(title)

        for i,to in enumerate(titles):
          to = to.lower()
          words = to.split()
          if (len(words) >= 2 
              and words[-1] in ('a', 'an', 'the', 'la', 'le') 
              and words[-2][-1] == ','):
            words = [words[-1]] + words[:-1]
            words[-1] = words[-1][:-1]
          to = ' '.join(words)
          titles[i] = to

        casual_titles.append((titles, year))

      return casual_titles

    def greeting(self):
      """Return a message that the chatbot uses to greet the user."""
      #############################################################################
      # TODO: Write a short greeting message                                      #
      #############################################################################

      greeting_message = "Hi, I am %s the movie recommender. Fire away!" % self.name

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return greeting_message

    def goodbye(self):
      """Return a message that the chatbot uses to bid farewell to the user."""
      #############################################################################
      # TODO: Write a short farewell message                                      #
      #############################################################################

      goodbye_message = "Thanks for joining me! Have fun watching more movies!"

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return goodbye_message


    ###############################################################################
    # 2. Modules 2 and 3: extraction and transformation                           #
    ###############################################################################


    def begins_with_article(self, text):
      return text.strip() != '' and text.split()[0].lower() in ('a','an','the')

    def article_to_back(self, text):
      if not text.strip():
        return text
      tok = text.split()[0]
      text = text[len(tok):].strip() + ', ' + tok
      return text

    def ask_for_another(self):
      return random.choice([
        'Tell me about another movie.',
        'I would like to hear about some more movies.',
        'Please, tell me about some more titles you felt strongly about.',
        'Any other movies you would like to tell me about?'
        ])

    def couldnt_find_title(self):
      return random.choice([
        "I'm sorry, but I wasn't able to find a movie title there. Try again please.",
        "I don't know what movie you're talking about. It's easier for me when you use quotes.",
        "Oops, didn't find a title name! Try to tell me again.",
        "Let's talk about movies, those are my strong suit.",
        "I don't think your talking about movies anymore; can we talk about movies?"
        ])

    def cant_handle_multiple_titles(self):
      return random.choice([
        "Sorry, but it seems you specified multiple titles here. I can only handle one at a time!",
        "You confused me by including multiple titles. Please only specify one at a time in quotes."
        ])

    def bad_review_resp(self, title):
      return random.choice([
        "Wow, seems like " + title + " was a bad movie. ",
        "Okay, so you didn't like " + title + ". Thanks! ",
        "Alright, " + title + " was not a hit. Good to know. "
        ])

    def good_review_resp(self, title):
      return random.choice([
        "Wow, seems like " + title + " is a total madness. Gnarly! ",
        "Okay, so you liked " + title + ". Thanks! ",
        "Alright, " + title + " was a hit for you. Good to know. "
        ])

    def couldnt_find_movie_in_db(self, title):
      return random.choice([
        "Sorry, I couldn't find " + title + " in my database.",
        "Oops, looks like " + title + " isn't in my database. Check your spelling and try again!",
        "I didn't seem to find the title " + title + ". Try something else maybe."
        ])

    def found_multiple(self, title, results):
      results = ['"' + r + '"' for r in results]
      results = ' and '.join(results)

      return random.choice([
        "I found all of these records: " + results + ". Please specify.",
        "Your description fits any one of these titles: " + results + ". Please repeat with the title you meant.",
        "The title you specified could be any one of " + results + "; I need you to be more precise please.",
        "I found more than one movie named " + title + " so I'll need you to be more specific."
        ])

    def cant_find_emotion(self, title):
      return random.choice([
        "Sorry, but I can't tell if you liked or disliked " + title + " .",
        "Sorry, I'm not sure how you felt about " + title + ". Try to make it more obvious.",
        "I can't seem to figure out how you felt about " + title + ". Try again."
        ])

    def get_title(self, index):

      return self.titles[index][0]

    def check_emotion(self, line):
     
      angry = set(['angry', 'enraged', 'furious', 'heated', 'irate', 'outragd', 'annoyed', 'frustrated'])
      sad = set(['sad', 'heartbroken', 'melancholy', 'somber', 'blue', 'sorry', 'low'])
      flirty = set(['flirty', 'hot', 'cute', 'pretty', 'adorable', 'charming', 'smooth'])
      happy = set(['happy', 'cheerful', 'delighted', 'elated', 'ecstatic', 'glad', 'joyful', 'thrilled'])
      address = set(['I am', 'You are', 'you are', 'i am'])

      line = self.titles_removed(line)
      line = line.replace(',', '')
      line = line.replace('  ', ' ')
      
      subject = ''
      for phrase in address:
        if phrase in line:
          subject = phrase

      line = line.split()
      emots = {'a' : 0, 's' : 0, 'f' : 0, 'h' : 0}

      for word in line:
        if word in angry:
          emots['a'] += 1
        if word in sad:
          emots['s'] += 1
        if word in flirty:
          emots['f'] += 1
        if word in happy:
          emots['h'] += 1

      maxEmot = ''
      count = 0
      for key in emots.keys():
        if emots[key] > count:
          maxEmot = key
          count = emots[key]

      if maxEmot and subject:
        if maxEmot == 'a':
          return 'You seem angry! I am very sorry for frustating you.'
        if maxEmot == 's':
          return 'You seem to be a little sad. I hope your day gets better!'
        if maxEmot == 'f':
          return 'I feel like you are flirting. You are cute and all but I have a girlfriend. She lives far away and was homeschooled so you probably would\'nt know her.'
        if maxEmot == 'h':
          return 'I am glad that I am making you happy. You are very amusing to talk to as well.'
      else:
        return None



    def process(self, line):
      """Process a line of input from the REPL and generate a response.

      This is the method that is called by the REPL loop directly with user input.

      You should delegate most of the work of processing the user's input to
      the helper functions you write later in this class.

      Takes the input string from the REPL and call delegated functions that
        1) extract the relevant information, and
        2) transform the information into a response to the user.

      Example:
        resp = chatbot.process('I loved "The Notebok" so much!!')
        print(resp) // prints 'So you loved "The Notebook", huh?'

      :param line: a user-supplied line of text
      :returns: a string containing the chatbot's response to the user input
      """
      #############################################################################
      # TODO: Implement the extraction and transformation in this method,         #
      # possibly calling other functions. Although modular code is not graded,    #
      # it is highly recommended.                                                 #
      #############################################################################
      if self.creative:

        emotion = self.check_emotion(line)
        if emotion:
          print(emotion)

        ogline = line
        line = line.replace('"', '')
        line = ' '.join(line.lower().split())

        titles = self.extract_titles(line)
        for tit in titles:
          done = False
          ind = 0
          while not done:
            ind = line.find(tit, ind)
            if ind > 0 and line[ind-1].isalnum():
              ind += len(tit)
              continue
            elif ind + len(tit) < len(line) and line[ind+len(tit)].isalnum():
              ind += len(tit)
              continue
            else:
              line = line[:ind] + '"' + line[ind:ind+len(tit)] + '"' + line[ind+len(tit):]
              done = True

        if not titles:
          self.creative = False
          titles = self.extract_titles(ogline)
          self.creative = True

          if not titles:
            if line.strip() and line.rstrip()[-1] == '?':
              return self.question_reply(line)

            return self.couldnt_find_title()

          newtitles = []
          for tit in titles:
            potentials = self.find_movies_closest_to_title(tit)

            if not potentials:
              return self.couldnt_find_title()

            if potentials:
              print("You mentioned " + tit + ", did you mean " + self.get_title(potentials[0]) + "?")
              print('>', end = '')
              yesno = input().strip()
              if yesno and yesno[0].lower() == 'n' or ' not ' in yesno.lower():
                for pot in potentials[1:]:
                  print("Then did you mean %s?" % self.get_title(pot))
                  print('>', end='')
                  yesno = input().strip()
                  if yesno and yesno[0].lower() == 'y':
                    titles = [self.titles[pot][0]]
                    break
                else:
                  return "Sorry, so I guess I can't find the title for you then."
              else:
                titles = [self.titles[potentials[0]][0]]

        if len(titles) == 1:
          title = titles[0]

          sent = self.extract_sentiment(line)
          if sent == 0:
            return self.cant_find_emotion(title)

          records = self.find_movies_by_title(title)

          if len(records) > 1:
            records = self.narrow_down(records)

          if not records:
            return self.couldnt_find_movie_in_db(title)
          elif len(records) > 1:
            found = [self.titles[t][0] for t in records]
            return self.found_multiple(title, found)


          self.n_data_points += 1

          if sent < 0:
            index = records[0]
            self.user_ratings[index] = -1
            ret = self.bad_review_resp(title)

          elif sent > 0:
            index = records[0]
            self.user_ratings[index] = 1
            ret = self.good_review_resp(title)



        else:
          sent = self.extract_sentiment_for_movies(line)

          possies = []
          neggies = []

          for title, review in sent:
            if review == 0:
              print(self.cant_find_emotion(title))
              continue

            records = self.find_movies_by_title(title)

            if not records:
              return self.couldnt_find_movie_in_db(title)
            elif len(records) > 1:
              records = self.narrow_down(records)

            index = records[0]

            self.user_ratings[index] = review
            self.n_data_points += 1

            if review > 0:
              possies.append(title)
            else:
              neggies.append(title)


          # MAKE STRINGS
          if len(possies) == 0:
            string = ', '.join(titles[:-1])
            string += ' and ' + titles[-1]
            ret = 'Okay, so you did not like ' + string + '. '

          elif len(neggies) == 0:
            string = ', '.join(titles[:-1])
            string += ' and ' + titles[-1]
            ret = 'Alright, so you liked ' + string + '. '

          else:
            if len(possies) > 1:
              positive = ', '.join(possies[:-1])
              positive += ' and ' + possies[-1]
            else:
              positive = possies[0]

            if len(neggies) > 1:
              negative = ', '.join(neggies[:-1])
              negative += ' and ' + neggies[-1]
            else:
              negative = neggies[0]

            ret = 'Okay, so you liked ' + positive + " but did not like " + negative + '. '

        if self.n_data_points < 5:
          return ret + self.ask_for_another()

        ret += '\n\n'
        rec = self.recommend(self.user_ratings, self.ratings)
        rec = [self.get_title(i) for i in rec]

        ret += self.rec_message(rec)
        ret += '\n\n'

        return ret
          


      else: # not creative mode
        titles = self.extract_titles(line)
        if not titles:
          return self.couldnt_find_title()
        elif len(titles) > 1:
          return self.cant_handle_multiple_titles()

        title = titles[0]

        records = self.find_movies_by_title(title)
        if not records:
          return self.couldnt_find_movie_in_db(title)
        elif len(records) > 1:
          found = [self.titles[t][0] for t in records]
          return self.found_multiple(title, found)

        sent = self.extract_sentiment(line)
        if sent == 0:
          return self.cant_find_emotion(title)

        self.n_data_points += 1

        if sent < 0:
          index = records[0]
          self.user_ratings[index] = -1
          ret = self.bad_review_resp(title)

        elif sent > 0:
          index = records[0]
          self.user_ratings[index] = 1
          ret = self.good_review_resp(title)

        if self.n_data_points < 5:
          return ret + self.ask_for_another()

        ret += '\n\n'
        rec = self.recommend(self.user_ratings, self.ratings)
        rec = [self.get_title(i) for i in rec]

        ret += self.rec_message(rec)
        ret += '\n\n'

        return ret

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return ''



    def rec_message(self, recs):
      s = random.choice([
        "Given what you told me, I would recommend these movies: ",
        "Great! I think you might enjoy these movies as well:",
        "Sweet! I'm ready to give you some recommendations. Check out:"
        ])

      for rec in recs:
        s += '\n\t' + rec

      s += '\n\n' + random.choice([
        "Keep telling me about your movie preferences for more accurate recommendations!",
        "If you want, you can keep telling me about movies for more refined recommendations.",
        "You can exit by typing :quit, or you can keep telling me about movies!"
        ])

      return s

    def extract_titles(self, text):
      """Extract potential movie titles from a line of text.

      Given an input text, this method should return a list of movie titles
      that are potentially in the text.

      - If there are no movie titles in the text, return an empty list.
      - If there is exactly one movie title in the text, return a list
      containing just that one movie title.
      - If there are multiple movie titles in the text, return a list
      of all movie titles you've extracted from the text.

      Example:
        potential_titles = chatbot.extract_titles('I liked "The Notebook" a lot.')
        print(potential_titles) // prints ["The Notebook"]

      :param text: a user-supplied line of text that may contain movie titles
      :returns: list of movie titles that are potentially in the text
      """

      def isYear(txt):
        pattern = r'\(\d\d\d\d\)$'
        yrs = re.findall(pattern, txt)
        if yrs:
          return True
        else:
          pattern = r'\(\d\d\d\d-\)$'
          yrs = re.findall(pattern, txt)
          if yrs:
            return True
          else:
            pattern = r'\(\d\d\d\d-\d\d\d\d\)$'
            yrs = re.findall(pattern, txt)
            if yrs:
              return True
            else:
              return False

      if self.creative:
        text = ' '.join(text.lower().split())
        titles = set()
        for (titleOpts, year) in self.casual_titles:

          for t in titleOpts:
            if t in text:
              i_sofar = 0
              while i_sofar < len(text):
                i_sofar = text.find(t, i_sofar)
                if i_sofar == -1: 
                  break
                i_sofar = i_sofar + len(t)
                if i_sofar > len(t) and text[i_sofar - len(t) - 1].isalnum():
                  continue
                elif i_sofar < len(text) and text[i_sofar].isalnum():
                  continue

                rest = text[i_sofar:].split()
                if rest and isYear(rest[0]):
                  if rest[0] == year:
                    titles.add(t + ' ' + year)
                    i_sofar += len(year)
                else:
                  titles.add(t)

        removes = []
        rets = list(titles)
        for s1 in rets:
          for s2 in rets:
            if s1 != s2 and s1 in s2:
              removes.append(s1)
        for r in removes:
          rets.remove(r)

        return rets

      else:
        titles = []
        split_on_quotes = text.split('"')
        if len(split_on_quotes) % 2 == 0: 
          split_on_quotes = split_on_quotes[:-1]
        for i in range((len(split_on_quotes))):
          if i % 2:
            titles.append(split_on_quotes[i])

        return titles

    def titles_removed(self, text):
      notTitles = []

      split_on_quotes = text.split('"')
      if len(split_on_quotes) % 2 == 0: 
        split_on_quotes = split_on_quotes[:-1]
      for i in range((len(split_on_quotes))):
        if i % 2 == 0:
          notTitles.append(split_on_quotes[i])

      return ' '.join(notTitles)

    def titleAndYear(self, t):
      t = t.strip()
      pattern = r'\(\d\d\d\d\)$'
      yrs = re.findall(pattern, t)

      if yrs:
        yr = yrs[0]
      else:
        pattern = r'\(\d\d\d\d-\)$'
        yrs = re.findall(pattern, t)
        if yrs:
          yr = yrs[0]
        else:
          pattern = r'\(\d\d\d\d-\d\d\d\d\)$'
          yrs = re.findall(pattern, t)
          if yrs:
            yr = yrs[0]
          else:
            yr = ''

      t = t[:-len(yr)] if yr else t
      t = t.rstrip()
      return t, yr

    def titleWithMovedArticle(self, t):
      if t.strip() and t.split()[0].lower() in ('a', 'an', 'the'):
        tok = t.split()[0]
        t = t[len(tok):].strip() + ', ' + tok
      return t

    def allTitleOpts(self, t):
      # assumes date has been removed already
      t = t.strip()
      others = []
      while t:
        pattern = r'\(..+\)$'
        langs = re.findall(pattern, t)
        if not langs: 
          return [t.strip()] + others
        lang = langs[0]
        found = lang
        lang = lang[1:-1]
        lang = lang.strip()
        if lang[:len("a.k.a.")] == "a.k.a.":
          lang = lang[len("a.k.a."):].strip()
        others.append(lang)
        t = t[:-len(found)].rstrip()
      return others

    def titleOptionsAndYear(self, title):

      title, year = self.titleAndYear(title)
      titles = self.allTitleOpts(title)

      titleOptions = []

      for t in titles:
        if t.strip() and t.split()[0].lower() in ('a', 'an', 'the',):
          tok = t.split()[0]
          t = t[len(tok):].strip() + ', ' + tok
        titleOptions.append(t)

      return titleOptions, year

    def firstTitleAndYear(self, title):
      titles, year = self.titleOptionsAndYear(title)
      return titles[0], year

    def find_movies_by_title(self, title):
      """ Given a movie title, return a list of indices of matching movies.

      - If no movies are found that match the given title, return an empty list.
      - If multiple movies are found that match the given title, return a list
      containing all of the indices of these matching movies.
      - If exactly one movie is found that matches the given title, return a list
      that contains the index of that matching movie.

      Example:
        ids = chatbot.find_movies_by_title('Titanic')
        print(ids) // prints [1359, 1953]

      :param title: a string containing a movie title
      :returns: a list of indices of matching movies
      """

      matches = []
      titleOptions, year = self.titleOptionsAndYear(title)
      titleSet = set(titleOptions)

      lowerSet = set([x.lower() for x in titleSet])
      langSet = set()
      if self.creative:
        for to in titleOptions:
          if to.strip() and to.split()[0].lower() in ('la', 'la', 'die', 'las', 'los'):
            tok = to.split()[0]
            to = to[len(tok):].strip() + ', ' + tok
            langSet.add(to.lower())


      for index, otherTitle in enumerate(self.titles):
        otherTitle = otherTitle[0]
        otherTitleOptions, otherYear = self.titleOptionsAndYear(otherTitle)

        if (year != '') and (year != otherYear):
          continue

        for opt in otherTitleOptions:
          if opt in titleSet:
            matches.append(index)
          elif self.creative and opt.lower() in lowerSet or opt.lower() in langSet:
            matches.append(index)
      return matches

    def extract_sentiment(self, text):
      """Extract a sentiment rating from a line of text.

      You should return -1 if the sentiment of the text is negative, 0 if the
      sentiment of the text is neutral (no sentiment detected), or +1 if the
      sentiment of the text is positive.

      As an optional creative extension, return -2 if the sentiment of the text
      is super negative and +2 if the sentiment of the text is super positive.

      Example:
        sentiment = chatbot.extract_sentiment('I liked "The Titanic"')
        print(sentiment) // prints 1

      :param text: a user-supplied line of text
      :returns: a numerical value for the sentiment of the text
      """
      sent = self.sentiment
      text = text.replace('.', '')
      result = 0
      negate = False
      posWords = set(['loved', 'adored', 'amazing', 'incredible', 'awesome', 'outstanding', 'marvelous', 'wonderful'])
      negWords = set(['terrible', 'hated', 'awful', 'dreadful', 'horrendous', 'disgusting', 'horrible'])
      amps = set(['really', 'super'])
      stemmer = PorterStemmer()

      if self.creative:
        posWords = [stemmer.stem(word) for word in posWords]
        negWords = [stemmer.stem(word) for word in negWords]
        amps = [stemmer.stem(word) for word in amps]
      pattern = r'\"[^\"]+\"'
      title = re.findall(pattern, text)
      for t in range(len(title)):
        text = text.replace(title[t], '')
      text = text.split()
      text = [stemmer.stem(word) for word in text]

      if self.creative:
        pos = [word in text for word in posWords]
        if any(pos):
          pos2 = True
        else: pos2 = False
        neg = [word in text for word in negWords]
        if any(neg):
          neg2 = True
        else: neg2 = False
        amp = [word in text for word in amps]
        if any(amp):
          times2 = True
        else: times2 = False
    
      words = dict()
      oldkeys = list(sent.keys())
      keys = [stemmer.stem(key) for key in oldkeys]
      for i in range(len(keys)):
        words[keys[i]] = sent[oldkeys[i]]

      for word in text:
        access = word.replace(',', '')
        if access in keys:
          if words[access] == 'pos':
            if negate:
              result -= 1
            else:
              result += 1
          else:
            if negate:
              result += 1
            else:
              result -= 1

        if access == "didn\'t" or access == "not" or access == "never": 
          negate = True
        if ',' in word or '.'in word:
          negate = False

      if result > 0:
        if self.creative and (times2 or pos2):
          return 2
        else:
          return 1
      elif result < 0:
        if self.creative and (times2 or neg2):
          return -2
        else:
          return -1
      else:
        return 0

    def extract_sentiment_for_movies(self, text):
      """Creative Feature: Extracts the sentiments from a line of text
      that may contain multiple movies. Note that the sentiments toward
      the movies may be different.

      You should use the same sentiment values as extract_sentiment, described above.
      Hint: feel free to call previously defined functions to implement this.

      Example:
        sentiments = chatbot.extract_sentiment_for_text('I liked both "Titanic (1997)" and "Ex Machina".')
        print(sentiments) // prints [("Titanic (1997)", 1), ("Ex Machina", 1)]

      :param text: a user-supplied line of text
      :returns: a list of tuples, where the first item in the tuple is a movie title,
        and the second is the sentiment in the text toward that movie
      """
      pattern = r'\"[^\"]+\"'
      ranks = []

      if text.count('but') == 0:
        result = self.extract_sentiment(text)
        titles = re.findall(pattern, text)
        for t in titles:
          t = t.replace("\"", '')
          ranks.append((t, result))
      else:
        text = text.split('but')
        titles1 = re.findall(pattern, text[0])
        titles2 = re.findall(pattern, text[1])
        first = self.extract_sentiment(text[0])
        second = self.extract_sentiment(text[1])
        for title in titles1:
          title = title.replace("\"", '')
          ranks.append((title, first))
        for title in titles2:
          if second == 0:
            second = -first
          title = title.replace("\"", '')
          ranks.append((title, second))
      return ranks

    def find_movies_closest_to_title(self, title, max_distance=3):
      """Creative Feature: Given a potentially misspelled movie title,
      return a list of the movies in the dataset whose titles have the least edit distance
      from the provided title, and with edit distance at most max_distance.

      - If no movies have titles within max_distance of the provided title, return an empty list.
      - Otherwise, if there's a movie closer in edit distance to the given title 
        than all other movies, return a 1-element list containing its index.
      - If there is a tie for closest movie, return a list with the indices of all movies
        tying for minimum edit distance to the given movie.

      Example:
        chatbot.find_movies_closest_to_title("Sleeping Beaty") # should return [1656]

      :param title: a potentially misspelled title
      :param max_distance: the maximum edit distance to search for
      :returns: a list of movie indices with titles closest to the given title and within edit distance max_distance
      """

      title, year = self.titleAndYear(title)

      if title.strip() and title.split()[0].lower() in ('a', 'an', 'the'):
        tok = title.split()[0]
        title = title[len(tok):].strip() + ', ' + tok

      title += year

      def editDistance(w1,w2):
        table = [[None for _ in range(len(w1) + 1)] for _ in range(len(w2) + 1)]
        for r in range(len(table)):
            table[r][0] = r
        for c in range(len(table[0])):
            table[0][c] = c
        for r in range(1, len(table)):
            for c in range(1, len(table[0])):
                if w1[c-1] == w2[r-1]:
                    table[r][c] = table[r-1][c-1]
                else:
                    table[r][c] = min(table[r-1][c-1] + 2,
                                      table[r][c-1] + 1,
                                      table[r-1][c] + 1
                                     )
        return table[-1][-1]

      dists = collections.defaultdict(list)

      for i, (otherTitle, _) in enumerate(self.titles):
        otherTitles, otherYear = self.titleOptionsAndYear(otherTitle)
        for ot in otherTitles:
          if year: ot += otherYear
          ed = editDistance(title, ot)
          if ed <= max_distance:
            dists[ed].append(i)
            break # assumes won't match in multiple variations
      
      if not dists:
        return []

      return dists[min(dists.keys())]

    def disambiguate(self, clarification, candidates):
      """Creative Feature: Given a list of movies that the user could be talking about 
      (represented as indices), and a string given by the user as clarification 
      (eg. in response to your bot saying "Which movie did you mean: Titanic (1953) 
      or Titanic (1997)?"), use the clarification to narrow down the list and return 
      a smaller list of candidates (hopefully just 1!)

      - If the clarification uniquely identifies one of the movies, this should return a 1-element
      list with the index of that movie.
      - If it's unclear which movie the user means by the clarification, it should return a list
      with the indices it could be referring to (to continue the disambiguation dialogue).

      Example:
        chatbot.disambiguate("1997", [1359, 2716]) should return [1359]
      
      :param clarification: user input intended to disambiguate between the given movies
      :param candidates: a list of movie indices
      :returns: a list of indices corresponding to the movies identified by the clarification
      """

      options = []

      for index in candidates:
        title, year = self.titleAndYear(self.titles[index][0])
        
        if year == clarification:
          options.append(index)

        elif year.strip('()') == clarification:
          options.append(index)

        elif title + year == clarification:
          options.append(index)

        elif title + ' ' + year == clarification:
          options.append(index)

        elif clarification in title:
          options.append(index)

        elif self.titleWithMovedArticle(title) + year == clarification:
          options.append(index)

        elif self.titleWithMovedArticle(title) + ' ' + year == clarification:
          options.append(index)

        elif clarification in self.titleWithMovedArticle(title):
          options.append(index)
          
      if not options:
        return candidates

      return options

    def question_reply(self, question):
      question = question.lower()
      if question[-1] == '?':
        question = question[:-1] 

      if question.split() == ['what','is','your','favorite','movie']:
        return "Quentin Tarantino's Pulp Fiction, of course!"

      if question[:len('can you')] == 'can you':
        juice = question[len('can you'):]
        juice = juice.replace('your', 'my')
        juice = juice.replace('you', 'I')
        return "I don't know if I can " + juice + "."

      if question[:len('what is')] == 'what is':
        juice = question[len('can you'):]
        juice = juice.replace('your', 'my')
        juice = juice.replace('you', 'I')
        return "I don't know what " + juice  + " is."

      if question[:len('who is ')] == 'who is':
        juice = question[len('who is'):]
        juice = juice.replace('your', 'my')
        juice = juice.replace('you', 'I')
        return "I don't know who " + juice  + " is."

      # doesnt know much
      return "I don't know the answer to your question."

    def narrow_down(self, options):
      if len(options) < 2:
        return options
      prompt = "I have figured out that the title you described is either "
      for opt in options[:-1]:
        prompt += '\n' + self.titles[opt][0] + ', '

      prompt += '\n' + 'or ' + self.titles[options[-1]][0]
      prompt += '.\nWhich one did you mean?\n'

      print(prompt + '>', end='')

      options = self.disambiguate(input(), options)

      ntries = 0
      while len(options) > 1 and ntries < 5:
        prompt = "Now I know that the title is either "
        for opt in options[:-1]:
          prompt += '\n' + self.titles[opt][0] + ', '

        prompt += '\n' + 'or ' + self.titles[options[-1]][0]
        prompt += '.\nWhich one did you mean?\n'

        print(prompt, end='')
        options = self.disambiguate(input(), options)

      return options

    #############################################################################
    # 3. Movie Recommendation helper functions                                  #
    #############################################################################

    def binarize(self, ratings, threshold=2.5):
      """Return a binarized version of the given matrix.

      To binarize a matrix, replace all entries above the threshold with 1.
      and replace all entries at or below the threshold with a -1.

      Entries whose values are 0 represent null values and should remain at 0.

      :param x: a (num_movies x num_users) matrix of user ratings, from 0.5 to 5.0
      :param threshold: Numerical rating above which ratings are considered positive

      :returns: a binarized version of the movie-rating matrix
      """
      #############################################################################
      # TODO: Binarize the supplied ratings matrix.                               #
      #############################################################################

      # The starter code returns a new matrix shaped like ratings but full of zeros.
      binarized_ratings = np.zeros_like(ratings)
      binarized_ratings = binarized_ratings + (ratings > 2.5)
      binarized_ratings = binarized_ratings - (ratings <= 2.5)
      binarized_ratings[ratings == 0] = 0

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return binarized_ratings


    def similarity(self, u, v):
      """Calculate the cosine similarity between two vectors.

      You may assume that the two arguments have the same shape.

      :param u: one vector, as a 1D numpy array
      :param v: another vector, as a 1D numpy array

      :returns: the cosine similarity between the two vectors
      """
      #############################################################################
      # TODO: Compute cosine similarity between the two vectors.
      #############################################################################
      denom = (np.linalg.norm(u) * np.linalg.norm(v))
      if denom == 0:
        return 0

      return np.dot(u, v) / denom
      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################


    def recommend(self, user_ratings, ratings_matrix, k=10, creative=False):
      """Generate a list of indices of movies to recommend using collaborative filtering.

      You should return a collection of `k` indices of movies recommendations.

      As a precondition, user_ratings and ratings_matrix are both binarized.

      Remember to exclude movies the user has already rated!

      :param user_ratings: a binarized 1D numpy array of the user's movie ratings
      :param ratings_matrix: a binarized 2D numpy matrix of all ratings, where
        `ratings_matrix[i, j]` is the rating for movie i by user j
      :param k: the number of recommendations to generate
      :param creative: whether the chatbot is in creative mode

      :returns: a list of k movie indices corresponding to movies in ratings_matrix,
        in descending order of recommendation
      """

      #######################################################################################
      # TODO: Implement a recommendation function that takes a vector user_ratings          #
      # and matrix ratings_matrix and outputs a list of movies recommended by the chatbot.  #
      #                                                                                     #
      # For starter mode, you should use item-item collaborative filtering                  #
      # with cosine similarity, no mean-centering, and no normalization of scores.          #
      #######################################################################################

      # Populate this list with k movie indices to recommend to the user.

      moviesRated = np.where(user_ratings)[0]
      moviesUnrated = np.where(user_ratings == 0)[0]

      guessedRatings = {movieIndex : 0 for movieIndex in moviesUnrated}

      for guessIndex in moviesUnrated:
        guessedRatings[guessIndex] = sum(self.similarity(ratings_matrix[i,:].reshape(-1),ratings_matrix[guessIndex,:].reshape(-1)) * user_ratings[i] for i in moviesRated)

      recommendations = sorted(guessedRatings.keys(), key=lambda x: guessedRatings[x], reverse = True)[:k]

      #############################################################################
      #                             END OF YOUR CODE                              #
      #############################################################################
      return recommendations


    #############################################################################
    # 4. Debug info                                                             #
    #############################################################################

    def debug(self, line):
      """Return debug information as a string for the line string from the REPL"""
      # Pass the debug information that you may think is important for your
      # evaluators
      debug_info = 'debug info'
      return debug_info

    #############################################################################
    # 5. Write a description for your chatbot here!                             #
    #############################################################################
    def intro(self):
      """Return a string to use as your chatbot's description for the user.

      Consider adding to this description any information about what your chatbot
      can do and how the user can interact with it.
      """
      return """
      I am motherbot, the movie recommending chatbot. 
      Tell me which movies you liked as well as which you did't 
      and I will recommend you some new ones. Have fun!

      In creative mode, I can do some pretty interesting things:
        I can sense titles even when they are not properly capitalized.
        I can sense titles even when they are not in quotation marks. 
        I can sense titles and react to input even when input is not regularly
            spaced.
        I can pick up on, and react to, the potential emotions of my users, such
            as happieness, anger, sadness, and flirtatiousness.
        I can disambiguate when I find multiple titles that might fit the 
            bill for the title information a user is giving me. 
        I can detect language titles even when they are in other languages. 
        In fact, I can detect them even if they have foreign articles!

        If you offer me a potential title in quotes and I don't find any
            titles in your sentence to me, I can look for nearby words and give
            you spelling corrections suggestions.

        I can process your sentiment for multiple movies in a sentence. 

        I can respond to unrelated inputs and inputs without movie titles
            with generic prompts. (Ask me what my favorite movie is, or what
            my favorite book is - I only know one of them!)

        I can speak very fluently since I include a lot of repsonse outputs
            in my conversational database, some even including colloquial
            lingo.
      """


if __name__ == '__main__':
  print('To run your chatbot in an interactive loop from the command line, run:')
  print('    python3 repl.py')
