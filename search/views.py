from django.http import JsonResponse
from django.shortcuts import render
from search.forms import MovieSearchForm
import imdb
import telegram
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, filters, Updater, Application, MessageHandler
import asyncio

ia = imdb.IMDb()

bot = telegram.Bot(token='YOUR_API_TOKEN')
app = ApplicationBuilder().token("YOUR TOKEN HERE").build()


def get_movies(query):
    results = ia.search_movie(query)
    movies = []
    for movie in results:
        movie_id = movie.movieID
        title = movie.get('title')
        year = movie.get('year')
        link = f'http://your-django-app.com/movies/{movie_id}/'
        movies.append({'title': title, 'link': link})
    return movies


def search_movies_tg(query):
    movies = get_movies(query)
    movie_list = '<ul>'
    for movie in movies:
        movie_list += f'<li><a href="{movie["link"]}">{movie["title"]}</a></li>'
    movie_list += '</ul>'
    return movie_list


async def handle_message(update, context):
    # text = update.message.text
    text = ' '.join(context.args)
    links = search_movies_tg(text)
    if links:
        message = '\n'.join(links)
    else:
        message = 'No movies found'
    context.bot.sendMessage(chat_id=update.effective_chat.id, text=message)
    await update.message.reply_text(message)


# updater = telegram.Updater(token='YOUR_API_TOKEN', use_context=True)
# updater.dispatcher.add_handler(telegram.MessageHandler(telegram.Filters.text, handle_message))
# updater.start_polling()
# updater.idle()
# app.add_handler(CommandHandler('query', handle_message))


def search_movie(request):
    if request.method == 'POST':
        form = MovieSearchForm(request.POST)
        if form.is_valid():
            title = form.cleaned_data['title']
            movies = ia.search_movie(title)
            return render(request, 'search_movie.html', {'form': form, 'movies': movies})
    else:
        form = MovieSearchForm()
    return render(request, 'search_movie.html', {'form': form})


def movie_detail(request, imdb_id):
    movie = ia.get_movie(imdb_id)
    poster_url = movie.get('cover url')
    print(movie.summary())
    return render(request, 'movie_detail.html', {'movie': movie, 'poster_url': poster_url})


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("TOKEN").build()

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
