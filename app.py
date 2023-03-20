# ----------------------------------------------------------------------------#
# Imports
# ----------------------------------------------------------------------------#

import logging
from datetime import datetime
from logging import FileHandler, Formatter

import babel
import dateutil.parser
from flask import Flask, flash, redirect, render_template, request, url_for
from flask_migrate import Migrate
from flask_moment import Moment
from sqlalchemy import or_

from config import Config
from forms import ArtistForm, ShowForm, VenueForm
from models import Artist, Show, Venue, db

# ----------------------------------------------------------------------------#
# App Config.
# ----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object(Config)
db.init_app(app)
migrate = Migrate(app=app, db=db)


# ----------------------------------------------------------------------------#
# Filters.
# ----------------------------------------------------------------------------#


def format_datetime(value, format="medium"):
    date = dateutil.parser.parse(value)
    if format == "full":
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == "medium":
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale="en")


app.jinja_env.filters["datetime"] = format_datetime


# ----------------------------------------------------------------------------#
# Controllers.
# ----------------------------------------------------------------------------#


@app.route("/")
def index():
    return render_template("pages/home.html")


#  Venues
#  ----------------------------------------------------------------


@app.route("/venues")
def venues():
    # TODO: replace with real venues data.
    all_venues = Venue.query.all()
    return render_template("pages/venues.html", venues=all_venues)


@app.route("/venues/search", methods=["POST"])
def search_venues():
    """Search for venues"""
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    #   search for Hop should return "The Musical Hop".
    #   search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "")
    data = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all()
    response = {"count": len(data), "data": data}
    return render_template(
        "pages/search_venues.html", results=response, search_term=search_term
    )


@app.route("/venues/<int:venue_id>")
def show_venue(venue_id):
    """shows the venue page with the given venue_id"""
    # TODO: replace with real venue data from the venues table, using venue_id
    venue = Venue.query.get_or_404(venue_id)
    past_shows = []
    upcoming_shows = []
    for show in venue.shows:
        temp_show = {
            "artist_id": show.artist_id,
            "artist_name": show.artist.name,
            "artist_image_link": show.artist.image_link,
            "start_time": show.start_time,
        }
        if datetime.strptime(show.start_time, "%Y-%m-%d %H:%M:%S") <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    data = vars(venue)  # Converts object to dict

    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)

    return render_template("pages/show_venue.html", venue=data)


#  Create Venue
#  ----------------------------------------------------------------


@app.route("/venues/create", methods=["GET"])
def create_venue_form():
    form = VenueForm()
    return render_template("forms/new_venue.html", form=form)


@app.route("/venues/create", methods=["POST"])
def create_venue_submission():
    # TODO: insert form data as a new Venue record in the db, instead
    form = VenueForm(request.form)
    # TODO: modify data to be the data object returned from db insertion
    try:
        venue = Venue()
        form.populate_obj(venue)
        db.session.add(venue)
        db.session.commit()
        # on successful db insert, flash success
        flash("Venue " + request.form["name"] + " was successfully listed!")

    except Exception as e:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash(
            "An error occurred. Venue " + request.form["name"] + " could not be listed."
        )
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.route("/venues/delete/<venue_id>")
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
    venue = Venue.query.get(venue_id)
    try:
        db.session.delete(venue)
        db.session.commit()
        flash("Successfully deleted")
    except Exception as e:
        db.session.rollback()
        flash("Failed to delete")
    finally:
        db.session.close()
    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    return redirect(url_for("index"))


#  Artists
#  ----------------------------------------------------------------
@app.route("/artists")
def artists():
    # TODO: replace with real data returned from querying the database
    artists_all = Artist.query.all()
    return render_template("pages/artists.html", artists=artists_all)


@app.route("/artists/search", methods=["POST"])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".
    search_term = request.form.get("search_term", "")
    data = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all()
    response = {"count": len(data), "data": data}
    return render_template("pages/search_artists.html", results=response)


@app.route("/artists/<int:artist_id>")
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # TODO: replace with real artist data from the artist table, using artist_id
    artist = Artist.query.get(int(artist_id))
    shows = artist.shows
    past_shows = []
    upcoming_shows = []

    for show in shows:
        temp_show = {
            "venue_id": show.venue_id,
            "venue_name": show.venue.name,
            "venue_image_link": show.venue.image_link,
            "start_time": show.start_time,
        }
        if datetime.strptime(show.start_time, "%Y-%m-%d %H:%M:%S") <= datetime.now():
            past_shows.append(temp_show)
        else:
            upcoming_shows.append(temp_show)

    data = vars(artist)

    data["past_shows"] = past_shows
    data["upcoming_shows"] = upcoming_shows
    data["past_shows_count"] = len(past_shows)
    data["upcoming_shows_count"] = len(upcoming_shows)

    return render_template("pages/show_artist.html", artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route("/artists/<int:artist_id>/edit", methods=["GET", "POST"])
def edit_artist_submission(artist_id):
    artist = Artist.query.get(artist_id)
    # TODO: populate form with fields from artist with ID <artist_id>
    form = ArtistForm(obj=artist)
    if form.validate_on_submit():
        # TODO: take values from the form submitted, and update existing
        # artist record with ID <artist_id> using the new attributes
        form.populate_obj(artist)  # Update the artist object with the new data

        try:
            db.session.commit()
            flash(f"Artist {artist.name} was successfully updated!")
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to update Artist {artist.name}: {e}")
        finally:
            db.session.close()

        return redirect(url_for("show_artist", artist_id=artist_id))

    return render_template("forms/edit_artist.html", form=form, artist=artist)


@app.route("/venues/<int:venue_id>/edit", methods=["GET", "POST"])
def edit_venue(venue_id):
    venue = Venue.query.get(venue_id)
    form = VenueForm(obj=venue)
    # TODO: populate form with values from venue with ID <venue_id>
    if form.validate_on_submit():
        form.populate_obj(venue)
        # TODO: take values from the form submitted, and update existing
        # venue record with ID <venue_id> using the new attributes
        try:
            db.session.commit()
            flash(f"{venue.name} was successfully updated")
        except Exception as e:
            db.session.rollback()
            flash(f"Failed to update {venue.name} - {e}")
        finally:
            db.session.close()

        return redirect(url_for("show_venue", venue_id=venue_id))

    return render_template("forms/edit_venue.html", form=form, venue=venue)


#  Create Artist
#  ----------------------------------------------------------------


@app.route("/artists/create", methods=["GET"])
def create_artist_form():
    form = ArtistForm()
    return render_template("forms/new_artist.html", form=form)


@app.route("/artists/create", methods=["POST"])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Artist record in the db, instead
    form = ArtistForm(request.form)
    try:
        artist = Artist()
        form.populate_obj(artist)
        db.session.add(artist)
        db.session.commit()
        # on successful db insert, flash success
        flash("Artist " + request.form["name"] + " was successfully listed!")
    except Exception as e:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash(
            "An error occurred. Artist "
            + request.form["name"]
            + " could not be listed. "
            + str(e)
        )
    finally:
        db.session.close()
    return render_template("pages/home.html")


#  Shows
#  ----------------------------------------------------------------


@app.route("/shows")
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    # all_shows = Show.query.join(Artist, Show.artist_id == Artist.id) \
    #     .join(Venue, Show.venue_id == Venue.id).all()
    all_shows = Show.query.all()
    data = []
    for show in all_shows:
        data.append(
            {
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
                "artist_id": show.artist_id,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.start_time,
            }
        )
    return render_template("pages/shows.html", shows=data)


# Search shows
@app.route("/shows/search", methods=["POST"])
def search_shows():
    # TODO: implement search o show with partial string search.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
    search_term = request.form.get("search_term", "")
    filter_shows = (
        Show.query.join(Artist, Show.artist_id == Artist.id)
        .join(Venue, Show.venue_id == Venue.id)
        .filter(
            or_(
                Artist.name.ilike(f"%{search_term}%"),
                Venue.name.ilike(f"%{search_term}%"),
            )
        )
        .all()
    )
    data = []
    for show in filter_shows:
        data.append(
            {
                "artist_image_link": show.artist.image_link,
                "artist_name": show.artist.name,
                "start_time": show.start_time,
                "artist_id": show.artist_id,
                "venue_id": show.venue_id,
                "venue_name": show.venue.name,
            }
        )
    response = {"count": len(data), "data": data}
    return render_template("pages/show.html", results=response, search_term=search_term)


@app.route("/shows/create")
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template("forms/new_show.html", form=form)


@app.route("/shows/create", methods=["POST"])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # TODO: insert form data as a new Show record in the db, instead
    form = ShowForm(request.form)
    try:
        new_show = Show()
        form.populate_obj(new_show)
        db.session.add(new_show)
        db.session.commit()
        # on successful db insert, flash success
        flash("Show was successfully listed!")
    except Exception as e:
        db.session.rollback()
        # TODO: on unsuccessful db insert, flash an error instead.
        flash(f"An error occurred. Show could not be listed. - {e}")
        # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template("pages/home.html")


@app.errorhandler(404)
def not_found_error(error):
    return render_template("errors/404.html"), 404


@app.errorhandler(500)
def server_error(error):
    return render_template("errors/500.html"), 500


if not app.debug:
    file_handler = FileHandler("error.log")
    file_handler.setFormatter(
        Formatter("%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]")
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info("errors")

# ----------------------------------------------------------------------------#
# Launch.
# ----------------------------------------------------------------------------#

# Default port:
if __name__ == "__main__":
    app.run()

# Or specify port manually:
"""
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
"""
