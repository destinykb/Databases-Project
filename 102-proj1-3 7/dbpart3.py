"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
# accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
import os
# accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, url_for
from datetime import datetime

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.139.8.30/proj1part2
#
# For example, if you had username ab1234 and password 123123, then the following line would be:
#
#     DATABASEURI = "postgresql://ab1234:123123@34.139.8.30/proj1part2"
#


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
with engine.connect() as conn:
    create_table_command = """
	CREATE TABLE IF NOT EXISTS test (
		id serial,
		name text
	)
	
	
	"""
    res = conn.execute(text(create_table_command))
    insert_table_command = """INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace')"""
    res = conn.execute(text(insert_table_command))
    # you need to commit for create, insert, update queries to reflect
    conn.commit()


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request
    (every time you enter an address in the web browser).
    We use it to setup a database connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()
    except:
        print("uh oh, problem connecting to database")
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/1.1.x/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#

# home page route
@app.route('/')
def homepage():
    """
    request is a special object that Flask provides to access web request information:

    request.method:   "GET" or "POST"
    request.form:     if the browser submitted a form, this contains the data in the form
    request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: https://flask.palletsprojects.com/en/1.1.x/api/#incoming-request-data
    """

    # DEBUG: this is debugging code to see what request looks like
    print(request.args)

    return render_template("homepage.html")

@app.route('/search')
def search():

    query = request.args.get('query', '')

    q_param = f"%{query}%"

    print(query)

    if not query:
        return render_template('search.html', results=[], query=query)

    performer_name = text("""
                    SELECT
                        performer_name,
                        performer_id
                    FROM Performer
    """)

    performer_cursor = g.conn.execute(performer_name)
    performers = [result[0] for result in performer_cursor]

    venue_name = text("""
                    SELECT
                        venue_name
                    FROM Venue        
    """)

    venue_cursor = g.conn.execute(venue_name)
    venues = [result[0] for result in venue_cursor]

    is_performer = False
    q_lower = query.lower()
    if any(q_lower in p.lower() for p in performers):
        print("PERFORMER SEARCH")
        is_performer = True
        performer_check_sql = text("""
                SELECT  
                    P.performer_name, 
                    AH.bio, 
                    AH.img
                FROM Performer P 
                JOIN artist_homepage AH ON P.performer_id = AH.performer_id
                WHERE P.performer_name ILIKE :q
                LIMIT 1
            """)
        performer_data = g.conn.execute(performer_check_sql, {"q": q_param}).fetchone()

        performer_info = {}
        if performer_data:
            performer_info = {
                "name": performer_data[0],
                "bio": performer_data[1],
                "image_url": performer_data[2]
            }

        performer_rating_sql = text("""
                SELECT average_rating
                FROM Performer
                WHERE performer_name ILIKE :q
                LIMIT 1
                """)

        performer_rating = float(g.conn.execute(performer_rating_sql, {"q": q_param}).fetchone()[0])

        sql_query = text("""
                SELECT 
                    V.venue_name,
                    V.city, 
                    V.country,
                    C.concert_date,
                    C.concert_time,
                    C.num_tix_avail,
                    C.tix_price
                FROM Performer P, Concert C, Venue V
                WHERE P.performer_id = C.performer_id
                    AND C.venue_id = V.venue_id
                    AND P.performer_name ILIKE :q

            """)

    elif any(q_lower in v.lower() for v in venues):
        print("VENUE SEARCH")
        sql_query = text("""
                        SELECT 
                            P.performer_name,
                            V.venue_name,
                            V.city, 
                            V.country,
                            C.concert_date,
                            C.concert_time,
                            C.num_tix_avail,
                            C.tix_price
                        FROM Performer P, Concert C, Venue V
                        WHERE P.performer_id = C.performer_id
                          AND C.venue_id = V.venue_id
                            AND V.venue_name ILIKE :q
                          
                    """)

    else:
        print("LAST ELSE")
        sql_query = text("""
                    SELECT 
                        P.performer_name, 
                        V.venue_name,
                        V.city, 
                        V.country,
                        C.concert_date,
                        C.concert_time,
                        C.num_tix_avail,
                        C.tix_price
                    FROM Performer P, Concert C, Venue V
                    WHERE P.performer_id = C.performer_id
                      AND C.venue_id = V.venue_id
                      AND (P.performer_name ILIKE :q
                           OR V.city ILIKE :q
                           OR V.venue_name ILIKE :q
                           OR C.concert_date::text ILIKE :q)
                """)

    cursor = g.conn.execute(sql_query, {"q": q_param})

    results = cursor.fetchall()

    print(results)
    cursor.close()

    '''
    if is_performer:
        return render_template(
            'search.html',
            results=results,
            query=query,
            performer_info=performer_info
        )
    '''

    if is_performer:
        return render_template(
            'search.html',
            results=results,
            query=query,
            performer_info=performer_info,
            performer_rating = performer_rating
        )

    else:
        return render_template('search.html', results=results, query=query)

@app.route('/ratings')
def ratings():
    query = request.args.get('artist')
    q_param = f"%{query}%"

    if not query:
        return render_template('ratings.html', ratings={}, query=query)

    avg_sql = text("""
                   SELECT ROUND(AVG(R.rating)::numeric, 1)
                   FROM Ratings R
                            JOIN Performer P ON P.performer_id = R.performer_id
                   WHERE P.performer_name ILIKE :q
                   """)
    avg_result = g.conn.execute(avg_sql, {"q": q_param}).fetchone()
    average_rating = avg_result[0] if avg_result and avg_result[0] is not None else None

    sql_query = text("""
        SELECT R.rating_id, C.firstName, P.performer_name, R.rating, R.reviews, R.date_written, R.time_written
        FROM Ratings R
        JOIN Performer P ON P.performer_id = R.performer_id
        JOIN Customer C on C.customer_id = R.customer_id
        WHERE P.performer_name ILIKE :q
        ORDER BY R.date_written DESC, R.time_written DESC
    """)

    results_cursor = g.conn.execute(sql_query, {"q": q_param})
    results = [{"rating_id": r[0], "customer": r[1], "artist": r[2], "rating": r[3], "reviews": r[4], "date": r[5], "time": r[6]} for r in results_cursor]

    results_cursor.close()
    print(results)
    return render_template("ratings.html",ratings=results, query=query, average_rating=average_rating)

@app.route('/leave_review', methods=['GET', 'POST'])
def leave_review():
    artist = request.args.get('artist', '')

    if request.method == 'POST':
        email = request.form.get('email')
        rating = request.form.get('rating')
        reviews = request.form.get('reviews')
        artist_name = request.form.get('artist')

        customer_sql = text("SELECT customer_id FROM Customer WHERE emails = :email")
        customer_result = g.conn.execute(customer_sql, {"email": email}).fetchone()

        if not customer_result:
            return "Email not associated with an account. Please use a registered email."

        customer_id = customer_result[0]

        performer_sql = text("SELECT performer_id FROM Performer WHERE performer_name = :name")
        performer_result = g.conn.execute(performer_sql, {"name": artist_name}).fetchone()

        if not performer_result:
            return f"Artist '{artist_name}' not found."

        performer_id = performer_result[0]
        next_id_sql = text("SELECT COALESCE(MAX(rating_id), 0) + 1 FROM Ratings")
        next_id = g.conn.execute(next_id_sql).scalar()

        sql_insert = text("""
            INSERT INTO Ratings (rating_id, customer_id, performer_id, rating, reviews, date_written, time_written)
            VALUES (
            :rating_id,
            (SELECT customer_id FROM Customer WHERE emails = :email),
            (SELECT performer_id FROM Performer WHERE performer_name = :artist),
            :rating,
            :reviews,
            CURRENT_DATE,
            CURRENT_TIME
            )
        """)

        g.conn.execute(sql_insert, {
            "rating_id": next_id,
            "email": email,
            "artist": artist_name,
            "rating": rating,
            "reviews": reviews
        })

        avg_sql = text("""
                       UPDATE Performer
                       SET average_rating = (SELECT ROUND(AVG(rating)::numeric, 1)
                                             FROM Ratings
                                             WHERE performer_id = :pid)
                       WHERE performer_id = :pid
                       """)
        g.conn.execute(avg_sql, {"pid": performer_id})
        g.conn.commit()

        return redirect(url_for('ratings', artist=artist_name))

    return render_template('leave_review.html', artist=artist)

#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
@app.route('/my_reviews', methods=['GET', 'POST'])
def my_reviews():
    if request.method == 'POST':
        email = request.form.get('email')

        sql_query = text("""
            SELECT R.rating_id, P.performer_name, R.rating, R.reviews, R.date_written, R.time_written
            FROM Ratings R
            JOIN Customer C ON R.customer_id = C.customer_id
            JOIN Performer P ON R.performer_id = P.performer_id
            WHERE C.emails = :email
            ORDER BY R.date_written DESC, R.time_written DESC
        """)
        results_cursor = g.conn.execute(sql_query, {"email": email})
        results = [{
            "rating_id": r[0],
            "artist": r[1],
            "rating": r[2],
            "reviews": r[3],
            "date": r[4],
            "time": r[5]
        } for r in results_cursor]
        results_cursor.close()

        return render_template("my_reviews.html", reviews=results, email=email)

    return render_template("my_reviews.html", reviews=None)

@app.route('/delete_review/<int:rating_id>', methods=['POST'])
def delete_review(rating_id):
    artist_name = request.form.get('artist')
    email = request.form.get('email')

    # Check authorization
    sql_check = text("""
        SELECT COUNT(*)
        FROM Ratings R
        JOIN Customer C ON R.customer_id = C.customer_id
        WHERE R.rating_id = :rating_id AND C.emails = :email
    """)
    authorized = g.conn.execute(sql_check, {"rating_id": rating_id, "email": email}).scalar()

    if not authorized:
        print("Invalid email — you can only delete your own reviews.")
        return redirect(url_for('my_reviews'))

    # Delete the review
    sql_delete = text("DELETE FROM Ratings WHERE rating_id = :rating_id")
    g.conn.execute(sql_delete, {"rating_id": rating_id})

    # Update the performer's average rating
    sql_update_avg = text("""
        UPDATE Performer
        SET average_rating = (
            SELECT ROUND(AVG(rating)::numeric, 1)
            FROM Ratings
            WHERE performer_id = (SELECT performer_id FROM Performer WHERE performer_name = :artist)
        )
        WHERE performer_name = :artist
    """)
    g.conn.execute(sql_update_avg, {"artist": artist_name})

    g.conn.commit()

    return redirect(url_for('my_reviews'))


@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    artist = request.args.get('artist')
    venue = request.args.get('venue')
    city = request.args.get('city')
    country = request.args.get('country')
    date = request.args.get('date')
    time = request.args.get('time')
    tickets = request.args.get('tickets')
    price = request.args.get('price')

    tickets_for_selection = min(int(tickets),10)
    ticket_quantity = request.args.get('ticket_quantity')


    return render_template(
        'checkout.html',
        artist=artist,
        venue=venue,
        city=city,
        country=country,
        date=date,
        time=time,
        tickets=tickets,
        price=price,
        ticket_quantity=ticket_quantity,
        tickets_for_selection=tickets_for_selection
    )


@app.route('/confirmation', methods=['GET', 'POST'])
def confirmation():
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    credit_card = request.form.get('cc_number')
    email = request.form.get('email')
    ticket_quantity = int(request.form.get('ticket_quantity'))
    price = int(request.form.get('price'))


    customer_sql = text("SELECT customer_id FROM Customer WHERE emails = :email")
    customer_result = g.conn.execute(customer_sql, {"email": email}).fetchone()

    if not customer_result:
        query_customer_id = text("SELECT MAX(customer_id) FROM Customer")
        customer_id = g.conn.execute(query_customer_id).fetchone()[0]
        customer_id += 1
        insert_sql = text("""
               INSERT INTO Customer (customer_id, firstname, lastname, credit_card_num, emails)
               VALUES (:customer_id, :first_name, :last_name, :credit_card, :email)
           """)
        g.conn.execute(insert_sql, {
            "customer_id": customer_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": email,
            "credit_card": credit_card
        })
        g.conn.commit()
    else:
        customer_id = customer_result[0]

    concert_date = request.form.get('date')
    concert_date = datetime.strptime(concert_date, "%Y-%m-%d").date()

    concert_time = request.form.get('time')
    concert_time = datetime.strptime(concert_time, "%H:%M:%S").time()
    performer = request.form.get('artist')
    venue_name = request.form.get('venue')

    concert_id_purchase = text("""
                                      SELECT
                                           C.concert_id
                                      FROM Concert C
                                      JOIN ( SELECT
                                                   venue_id
                                               FROM Venue
                                               WHERE venue_name = :venue_name) V ON C.venue_id = V.venue_id
                                       JOIN (SELECT
                                                   performer_id
                                               FROM Performer
                                               WHERE performer_name = :performer) P ON C.performer_id = P.performer_id
                                       WHERE C.concert_date = :concert_date
                                         AND C.concert_time = :concert_time
                                         AND C.tix_price = :price
                                         """)

    concert_id = g.conn.execute(concert_id_purchase, {
        "venue_name": venue_name,
        "performer": performer,
        "concert_date": concert_date,
        "concert_time": concert_time,
        "price": price
    }).fetchone()[0]

    for i in range(int(ticket_quantity)):
        query_max_ticketid = text("SELECT MAX(ticket_id) FROM Tickets")
        max_ticket_id = g.conn.execute(query_max_ticketid).fetchone()[0]
        max_ticket_id += 1

        date_time = datetime.now()
        date_purchase = date_time.strftime("%Y-%m-%d")
        time_purchase = date_time.strftime("%H:%M:%S")

        insert_tickets_sql = text("""
                   INSERT INTO Tickets (ticket_id, customer_id, concert_id, date_purchased, time_purchased)
                   VALUES (:max_ticket_id, :customer_id, :concert_id, :date_purchase, :time_purchase)
               """)
        g.conn.execute(insert_tickets_sql, {
            "max_ticket_id": max_ticket_id,
            "customer_id": customer_id,
            "concert_id": concert_id,
            "date_purchase": date_purchase,
            "time_purchase": time_purchase
        })

    tix_avail_before_purchase = text(""" SELECT num_tix_avail FROM Concert WHERE concert_id = :concert_id """)
    tix_avail = g.conn.execute(tix_avail_before_purchase, {"concert_id": concert_id}).fetchone()[0]
    tix_avail -= ticket_quantity

    reduce_tix = text("""
                   UPDATE Concert
                   SET num_tix_avail = :tix_avail
                   WHERE concert_id = :concert_id
               """)
    g.conn.execute(reduce_tix, {
        "tix_avail": tix_avail,
        "concert_id": concert_id
    })
    g.conn.commit()

    return render_template('confirmation.html',
                           name=first_name,
                           email=email)

@app.route('/before_confirmation', methods=['POST', 'GET'])
def before_confirmation():

    ticket_quantity = int(request.form.get('ticket_quantity'))
    country = request.form.get('country')
    artist = request.form.get('artist')
    venue = request.form.get('venue')
    city = request.form.get('city')
    price = int(request.form.get('price'))
    num_tix_avail = int(request.form.get('tickets'))
    total_price = price * ticket_quantity
    concert_date = request.form.get('date')
    concert_date = datetime.strptime(concert_date, "%Y-%m-%d").date()

    concert_time = request.form.get('time')
    concert_time = datetime.strptime(concert_time, "%H:%M:%S").time()


    return render_template(
        'before_confirmation.html',

        artist=artist,
        venue=venue,
        city=city,
        country=country,
        date=concert_date,
        time=concert_time,
        price=price,
        ticket_quantity=ticket_quantity,
        total_price=total_price,
        num_tix_avail=num_tix_avail

    )



if __name__ == "__main__":
    import click


    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print("running on %s:%d" % (HOST, PORT))
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

run()

