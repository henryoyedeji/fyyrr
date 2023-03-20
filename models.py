from flask_sqlalchemy import SQLAlchemy

# TODO: connect to a local postgresql database
db = SQLAlchemy()


# ----------------------------------------------------------------------------#
# Models.
# ----------------------------------------------------------------------------#


class Venue(db.Model):
    __tablename__ = "Venue"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.JSON)
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text(), default="Not seeking artist right now")
    website_link = db.Column(db.String(120))
    shows = db.relationship("Show", backref="venue", lazy="joined", cascade="all, delete")


class Artist(db.Model):
    __tablename__ = "Artist"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.JSON)
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(500))

    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    website_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.Text(), default="Not seeking venues right now")
    shows = db.relationship("Show", backref="artist", lazy="joined", cascade="all, delete")


# TODO Implement Show and Artist models, and complete all model relationships
#  and properties, as a database migration.
class Show(db.Model):
    __tablename__ = "Show"

    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey("Venue.id"))
    artist_id = db.Column(db.Integer, db.ForeignKey("Artist.id"))
    start_time = db.Column(db.String(200))
