import psycopg2
import psycopg2.extras
import datetime
import time
from flask import Flask, render_template, request, g
from random import randint
app = Flask(__name__)

IP_ADDR = "35.194.34.244"


@app.route('/')
def homepage():
    return render_template("homepage.html")


@app.route('/view-item', methods=['get'])
def view_item():
    db = get_db()
    cursor = db.cursor()
    sql = "select * from items"
    cursor.execute(sql)
    items=cursor.fetchall()
    return render_template("view-item.html", entries=items)


@app.route('/auctions', methods=['get', 'post'])
def auctions():
    if request.args:
        itemid = request.args.get('itemid')
        db = get_db()
        cursor = db.cursor()
        cursor1 = db.cursor()
        cursor2 = db.cursor()
        cursor3 = db.cursor()
        cursor4 = db.cursor()
        sql_query = "select * from auction where itemselling=" + itemid
        cursor.execute(sql_query)
        row = cursor.fetchall()
        #debug(row)
        if len(row) > 0:
            auctionid = row[0][0]
            #debug(auctionid)
            sql1 = "select * from bid where auctionid=" + str(auctionid)\
                + " Order by bidprice"
            #debug(sql1)
            cursor1.execute(sql1)
            bids = cursor1.fetchall()
            finalprice = bids[len(bids)-1][2]
            sql3 = "select * from chat where auctionid=" + str(auctionid)
            #debug(sql3)
            cursor3.execute(sql3)
            chats = cursor3.fetchall()
            #debug(bids)
            if "step" not in request.form:
                return render_template("auctions.html", step="no bid", fp=finalprice, auction=row[0], bids=bids, chats=chats)
            elif request.form["step"] == "add_entry":
                sql2 = "insert into bid(auctionId, bidder, bidPrice, bidTime) values ("\
                    + "'" + str(auctionid) + "'," + "'" + request.args.get("user") + "',"\
                    + "'" + request.form["bidamount"] + "', now())"
                #debug(sql2)
                cursor2.execute(sql2)
                db.commit()
                cursor1.execute(sql1)
                bids = cursor1.fetchall()
                finalprice = bids[len(bids)-1][2]
                return render_template("auctions.html", fp=finalprice, auction=row[0], bids=bids, chats=chats)
            elif request.form["step"] == "add_chat":
                sql4 = "insert into chat(chatText, chatTime, chatter, auctionId) values ("\
                    + "'" + request.form["chattext"] + "', now(), '"\
                    + request.args.get("user") + "','" + str(auctionid) + "'" + ")"
                #debug(sql4)
                cursor4.execute(sql4)
                db.commit()
                cursor3.execute(sql3)
                chats = cursor3.fetchall()
                return render_template("auctions.html", fp=finalprice, auction=row[0], bids=bids, chats=chats)
        else:
            return render_template("auctions.html", item=itemid, auction=row)
    else:
        return render_template("auctions.html")
    
@app.route("/view-friends", methods=['get', 'post'])
def friends():
    db=get_db()
    cursor = db.cursor()
    sql_query = "SELECT friend1 FROM friends WHERE friend2="+"'" + request.args.get('user')+ "'" + "UNION SELECT friend2 FROM friends WHERE friend1="+"'" + request.args.get('user')+ "'"
    cursor.execute(sql_query)
    data = cursor.fetchall()
    return render_template("view-friends.html", data = data)

@app.route('/add-friend', methods=['get', 'post'])
def add_friend():
    if 'friendrequest' not in request.form:
        return render_template("add-friend.html", friendrequest="notadded")
    else:
        now = str(datetime.now())
        db = get_db()
        cursor = db.cursor()
        cursor.execute("insert into friends(friend1, friend2, dateAdded) values (%s, %s, %s)",
                   [request.args.get('user'), request.form["friend2"], now])
        db.commit()
        return render_template("add-friend.html", friendrequest="added")

@app.route('/delete-friend', methods=['get', 'post'])
def delete_friend():
    if 'frienddelete' not in request.form:
        return render_template("delete-friend.html", frienddelete="notdeleted")
    else:
        now = str(datetime.now())
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM friends WHERE (friend1="+"'"+request.args.get('user')+"'"+"AND friend2="+"'"+request.form["friend"]+"'"+") OR (friend1="+"'"+request.form["friend"]+"'"+" AND friend2="+"'"+request.args.get('user')+"'"+")")
        db.commit()
        return render_template("delete-friend.html", frienddelete="deleted")
    
@app.route('/post-item', methods=['get', 'post'])
def post_item():
    if 'item' not in request.form:
        return render_template("post-item.html", item="notposted")
    else:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("insert into items(itemName, description, startPrice, ownedBy) values (%s, %s, %s, %s)",
                   [request.form["itemName"], request.form["itemdesc"], request.form["startingprice"], request.args.get('user')])
        db.commit()
        return render_template("post-item.html", item ="posted")
    

@app.route('/create-account', methods=['get', 'post'])
def create_account():
    if 'account' not in request.form:
        return render_template("create-account.html", account="notmade")
    else:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("insert into users (email, username) values (%s, %s)",
                   [request.form["email"], request.form["username"]])
        db.commit()
        return render_template("create-account.html", account="accountmade")


@app.route('/sign-in', methods=['get', 'post'])
def sign_in():
    if 'credentials' not in request.form:
        return render_template("sign-in.html", credentials="no")
    else:
        db = get_db()
        cursor = db.cursor()
        username = str(request.form["username"])
        email = str(request.form["email"])
        sql_query = "select * from users" + \
            " where username='" + username + "' and " + \
            "email like '" + email + "'"
        debug(sql_query)

        cursor.execute(sql_query)
        user = cursor.fetchall()
        debug(user)
        return render_template("sign-in.html", credentials="yes", name=user[0][1], email=user[0][0])


@app.route('/user-home')
def user_home():
  return render_template("user-home.html")

@app.route('/messages',methods= ['get', 'post'])
def messages():
    db = get_db()
    cursor = db.cursor()
    cursor2 = db.cursor()
    cursorForID = db.cursor()
    idSetQuery= "SELECT setval('message_messageId_seq', (SELECT max(message.messageId) FROM message)); "
    cursorForID.execute(idSetQuery)
    message_query = 'SELECT * FROM message WHERE senderID='+ "'" + request.args.get('user')+ "'" + ' OR receiverID='+ "'" + request.args.get('user')+ "'" + " ORDER BY messTime"

    ############## Section for Writing entries ##################

    if "step" not in request.form:
        cursor.execute(message_query)
        data = cursor.fetchall()
        return render_template('messages.html', data=data, usern=request.args.get('user'), step="compose_entry")

    # Step 2, add blog post to database.
    elif request.form["step"] == "add_entry":
        sql2 = "insert into message(messTime, messText, senderID, receiverID) values ("\
            +"now(),'"+request.form["content"]+"','" \
            + request.args.get('user') + "','" + request.form["receiver"] + "'" + ")"
        debug(sql2)
        cursor.execute(message_query)
        data = cursor.fetchall()
        cursor2.execute(sql2)
        db.commit()
        cursor.execute(message_query)
        data = cursor.fetchall()
        return render_template('messages.html', data=data, usern=request.args.get('user'), step="add_entry")


@app.route("/search-item", methods=["get", "post"])
def search():
    if "query" not in request.form:
        return render_template("search-item.html")
    else:
        db = get_db()
        cursor = db.cursor()
        query = str(request.form["query"])
        sql_query = "select * from item_types natural join items natural join category" + \
            " where LOWER(catname)=LOWER('" + query + "') or " + \
            "LOWER(itemname) like LOWER(" + "'%" + query + "%') or " + \
            "LOWER(description) like LOWER('%" + query + "%')"
        cursor.execute(sql_query)
        rows = cursor.fetchall()
        return render_template("search-item.html", entries=rows)

# ------------------------------------------

# Database handling


def connect_db():
    """Connects to the database."""
    debug("Connecting to DB.")
    conn = psycopg2.connect(host=IP_ADDR, user="postgres", password="rhodes"
        , dbname="exchangedb", cursor_factory=psycopg2.extras.DictCursor)
    return conn


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'pg_db'):
        g.pg_db = connect_db()
    return g.pg_db


@app.teardown_appcontext
def close_db(error):
    """Closes the database automatically when the application
    context ends."""
    debug("Disconnecting from DB.")
    if hasattr(g, 'pg_db'):
        g.pg_db.close()


def debug(s):
    """Prints a message to the screen if FLASK_DEBUG is set."""
    if app.config['DEBUG']:
        print(s)
