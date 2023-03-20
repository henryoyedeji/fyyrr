from app import app, db, Artist

artist_1 = Artist(name='The hit boys', city='florida', state='FL', phone='1223838393',
                  image_link='https://images.pexels.com/photos/14875251/pexels-photo-14875251.jpeg',
                  genres=['Pop', 'Soul'], facebook_link='https://facebook.com', website_link='https://webomatrix.io')

try:
    with app.app_context():
        db.session.add(artist_1)
        db.session.commit()
    print("Successfully commited")

except:
    db.session.rollback()
    print("failed to commit")