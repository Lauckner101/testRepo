import sqlite3
import math
from datetime import datetime
from random import randint
from random import seed
from getpass import getpass  # hides typed passwords

"""
:param usr_id: usr_id corresponding to usr in users table
:returns: True if id is NOT in the db, False if id IS in the db
"""
def missing_id(usr_id):  # returns true if id is not present in database, false otherwise
    id_request = '''
                  SELECT usr
                  FROM users
                  WHERE usr = ?;
                 '''

    c.execute(id_request, (usr_id,))  # need goofy comma to convince the computer what I want to pass
    contains_usr = c.fetchone()  # will return a Nonetype if where clause fails

    if contains_usr is None:
        return True
    else:
        return False


"""
:param tweet_id: tweet_id corresponding to tid in tweets table
:returns: True if tid is NOT in the db, False if tid IS in the db
"""
def missing_tweet(tweet_id):
    tid_request = '''
                   SELECT tid
                   FROM tweets
                   WHERE tid = ?;
                  '''

    c.execute(tid_request, (tweet_id,))
    contains_tid = c.fetchone()

    if contains_tid is None:
        return True
    else:
        return False


"""
:returns tweid: A tid that IS present in the db
"""
def select_tid():
    valid_tweet = True
    while valid_tweet:
        tweid = input(" Please input the tweet id you would like to use\n>").lower().strip()
        valid_tweet = missing_tweet(tweid)

    return tweid


"""
:returns: Nothing, prints to the screen
"""
def login_screen():
    welcome_str = " Welcome to Mini Project 1 DB Login Screen"
    print('=' * 44)
    print(welcome_str)
    print("\n For returning users please type (Log)in\
           \n For new users please type       (R)egister\
           \n To exit please type             (Q)uit")
    print('=' * 44)


"""
:returns: Nothing, prints to the screen
"""
def interface_screen():
    interface_str = "              Welcome to your dashboard\n"
    print(" ")
    print('=' * 52)
    print(interface_str)
    print(" To make a search please type           (S)earch\
         \n To compose a tweet please type         (C)ompose\
         \n To retweet a tweet please type         (R)etweet\
         \n To show your followers please type:    (L)ist\
         \n To show followed tweets/retweets type: (F)ollowing\
         \n To logout please type                  (Log)out")
    print('=' * 52)


"""
:returns usr_id: usr_id corresponding to a valid usr_id pwd pair contained on the db
:returns status: True if correct credentials entered, False if not
"""
def login():
    usr_id = input(" usr_id: ")
    pwd = getpass(" pwd: ")
    status = False

    pwd_request = '''
                  SELECT pwd
                  FROM users
                  WHERE usr = ?;
                  '''
    c.execute(pwd_request, (usr_id,))
    db_pwd = c.fetchone()
    if pwd == db_pwd[0]:
        status = True

    return (usr_id, status)


"""
:returns reg_id: reg_id corresponding to a newly added valid usr on the db
:returns status: True if succesfully registered, False if not
"""
def register():
    INT_MAX = 2147483647
    seed(datetime.now().timestamp())
    contains_usr = False
    status = False
    while not contains_usr:
        reg_id = randint(0, INT_MAX)
        contains_usr = missing_id(reg_id)

    name = input(" name: ").strip()
    pwd = getpass(" pwd: ").strip()
    email = input(" Please input your email: ")
    phone = input(" Please input your phone: ")
    print("\n Your user id is: " + str(reg_id) + " please write it down\n")
    profile = (reg_id, name, email, phone, pwd)
    status = True
    registration_command = '''
                            INSERT INTO users (usr, name, email, phone, pwd)
                            VALUES (?, ?, ?, ?, ?);
                           '''
    c.execute(registration_command, profile)
    connection.commit()

    return (reg_id, status)


"""
:param usr: usr corresponding to the currently signed in usr
:param tid: tid corresponding to a valid tid to be retweeted
:returns: Nothing
"""
def retweet(usr, tid):
    c.execute("SELECT writer_id FROM tweets WHERE tid = ?", (tid,))
    writer_id = c.fetchone()
    rdate = datetime.today().strftime('%Y-%m-%d')
    c.execute("INSERT INTO retweets (tid, retweeter_id, writer_id, spam, rdate) VALUES (?, ?, ?, 0, ?);", (tid, usr, writer_id[0], rdate))
    connection.commit()


"""
:param user_id: user_id corresponding to the currently signed in user
:param replyto_tid: If tweet is a reply this is populated with a valid tid
:returns: Nothing
"""
def compose_tweet(user_id, replyto_tid=None):
    # Prompt the user to enter the tweet text
    tweet_text = input("\n Enter your tweet: ")

    # uses split() to extract # and filter out words starting with #
    words = tweet_text.split()
    hashtags = [i[1:].lower()
                for i in words
                if i.startswith('#') and len(i) > 1]

    # Insert the tweet into the tweets table
    try:
        # new tweet id
        c.execute("SELECT MAX(tid) + 1 FROM tweets")
        tweet_id = c.fetchone()[0]
        if tweet_id is None:
            tweet_id = 1

        # tweet date and time
        tdate = datetime.today().strftime('%Y-%m-%d')
        ttime = datetime.now().time().strftime('%H:%M:%S')

        # insert the tweet into the tweets table
        c.execute("""
            INSERT INTO tweets (tid, writer_id, text, tdate, ttime, replyto_tid)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (tweet_id, user_id, tweet_text, tdate, ttime, replyto_tid))

        # update hashtag_mentions table with the hashtag from the tweet
        for hashtag in hashtags:
            c.execute("""
                INSERT INTO hashtag_mentions (tid, term)
                VALUES (?, ?)
            """, (tweet_id, hashtag))

        # successful transaction
        connection.commit()
        print("\n Tweet successfully has been posted!\n")

    except sqlite3.Error as e:
        # Rollback in case of an error
        connection.rollback()
        print(f"An error has occurred: {e}")


"""
:param usr: usr corresponding to the user that will be selected
:returns data: list containing the user's: number of tweets, number of followers, number of followees, and all the user's tweets
"""
def select_user(usr):
    numberOfTweetsCommand = "SELECT COUNT(*) FROM tweets WHERE writer_id = ?;"
    numberOfFollowersCommand = "SELECT COUNT(*) FROM follows WHERE flwee = ?;"
    numberOfFolloweesCommand = "SELECT COUNT(*) FROM follows WHERE flwer = ?;"
    mostRecentTweetsCommand = """
                              SELECT t.tid, t.tdate, t.ttime, t.text
                              FROM tweets t
                              LEFT JOIN retweets r ON t.writer_id = r.retweeter_id
                              WHERE t.writer_id = ?
                              ORDER BY t.tdate DESC, t.ttime DESC;
                              """

    c.execute(numberOfTweetsCommand, (usr,))
    numberOfTweets = c.fetchone()

    c.execute(numberOfFollowersCommand, (usr,))
    numberOfFollowers = c.fetchone()

    c.execute(numberOfFolloweesCommand, (usr,))
    numberOfFollowees = c.fetchone()

    c.execute(mostRecentTweetsCommand, (usr,))

    allTweets = c.fetchall()
    data = (numberOfTweets[0], numberOfFollowers[0], numberOfFollowees[0], allTweets)
    return data


"""
:param usr: Currently signed in usr
:param usrToFollow:
"""
def follow_user(usr, usrToFollow):
    c.execute("INSERT INTO follows (flwer, flwee, start_date) VALUES (?, ?, DATE('now'));", (usr, usrToFollow))

    connection.commit()


"""
:param usr: usr to list followers of
:returns rows: A list containing the usr_id, name, and email of all of the users followers
:returns pagesCount: Number of pages that the list takes up
:returns item_count: The item count!
"""
def list_followers(usr):
    c.execute("SELECT u.usr, u.name, u.email FROM follows f, users u WHERE f.flwee = ? AND f.flwer = u.usr;", (usr,))
    rows = c.fetchall()
    item_count = len(rows)
    pagesCount = math.ceil(item_count/5)

    return rows, pagesCount, item_count


"""
:param usr: Currently signed in usr
:returns tweets_and_retweets: List containing all the tweets and retweets of the users the currently signed in user follows
                              or returns a Nonetype if the user does not follow any other users
"""
def followed_tweets(usr):
    followed_tweets_query = """
                            SELECT t.tid, t.tdate, t.ttime, t.text
                            FROM follows f
                            LEFT JOIN tweets t ON f.flwee = t.writer_id
                            WHERE flwer = ?
                            ORDER BY t.tdate DESC, t.ttime DESC;
                            """
    followed_retweets_query = """
                              SELECT r.tid, r.rdate, t.ttime, t.text
                              FROM retweets r
                              LEFT JOIN follows f ON r.retweeter_id = f.flwee
                              LEFT JOIN tweets t ON r.tid = t.tid
                              WHERE flwer  = ?
                              ORDER BY r.rdate DESC, t.ttime DESC;
                              """
    ALLOWED = True
    c.execute(followed_tweets_query, (usr,))
    tweets = c.fetchall()
    tweets = [("Tweet", t[0], t[1], t[2], t[3]) for t in tweets]
    c.execute(followed_retweets_query, (usr,))
    retweets = c.fetchall()
    retweets = [("Retweet", r[0], r[1], r[2], r[3]) for r in retweets]
    for tweet in tweets:
        for elem in tweet:
            if elem is None:
                ALLOWED = False
    for retweet in retweets:
        for elem in retweet:
            if elem is None:
                ALLOWED = False
    if ALLOWED:
        tweets_and_retweets = tweets + retweets
        tweets_and_retweets.sort(key=lambda x: (x[2], x[3]), reverse=True)
        return tweets_and_retweets
    else:
        return None


"""
:param usr: Currently signed in usr
:returns userData: List containing the number of tweets, followers, and other users this user follows
"""
def see_user_information(usr):
    userData = select_user(usr)
    # add user email and name to this data
    print("Tweets: " + str(userData[0]) + " | Followers: " +  str(userData[1]) + " | Follows: " + str(userData[2]))
    print("Most Recent Tweets: ")

    num_item_to_display = 3
    if (userData[0] < 3):
        num_item_to_display = userData[0]

    for i in range(num_item_to_display):
        print(userData[3][i])

    return userData


"""
:param usr: User to select and or follow
:param sel:
:returns: Nothing
"""
def select_and_or_follow_user(usr, sel):
    page = 0
    page_type = 'm'
    SELECTING = True
    match sel:
        case 'sel' | 'select':
            sel_usr = input(" Please enter the user_id to select\n>").lower().strip()
            while missing_id(sel_usr):
                sel_usr = input(" Please enter a valid user_id to select\n>").lower().strip()
            user_data = see_user_information(sel_usr)
            while SELECTING:
                print('=' * 50)
                print(" To follow this user type:               (F)ollow\
                     \n To see more tweets from this user type: (M)ore\
                     \n To return to the previous menu type:    (R)eturn")
                print('=' * 50)
                choice = input("\n>").lower().strip()
                match choice:
                    case 'f' | 'follow':
                        print("You have followed: " + sel_usr)
                        follow_user(usr, sel_usr)
                    case 'm' | 'more':
                        page_count = math.ceil(user_data[0]/5)
                        while SELECTING:
                            SELECTING, page = display_page(page, user_data[0], page_count, user_data[3], page_type, usr, 1)
                    case 'r' | 'return':
                        SELECTING = False
                    case _:
                        print(" Please input a valid selection")

        case 'f' | 'follow':
            sel_usr = input(" Please enter the user_id to follow\n>").lower().strip()
            while missing_id(sel_usr):
                sel_usr = input(" Please enter a valid user_id to follow\n>").lower().strip()
            follow_user(usr, sel_usr)


"""
:param keyword: A keyword to search users with
:returns ret: A list containing the searched for users id's and names, or if no results a None
:returns user_count:
:returns page_count:
"""
def search_user(keyword):
    keyword = "%" + keyword + "%"
    search_user_command = '''
                          SELECT usr, name
                          FROM users
                          WHERE name like ?
                          GROUP BY usr, name
                          ORDER BY LENGTH(name) ASC;
                          '''
    c.execute(search_user_command, (keyword,))  # need funny comma to make a tuple
    ret = c.fetchall()
    user_count = len(ret)
    page_count = math.ceil(user_count/5)

    return ret, user_count, page_count


"""
:param keyword: A keyword to search tweets with
:returns tweetList: A list containing all matching tweets, or None if no results
"""
def select_tweet(keyword):
    hashtag = "#"+keyword.lower()
    keyword = "% " + keyword.lower() + " %"

    tweets = """
             SELECT t.tid, t.tdate, t.ttime, t.text
             FROM tweets t
             LEFT JOIN hashtag_mentions h ON t.tid = h.tid
             LEFT JOIN retweets r ON t.tid = r.tid
             WHERE ' ' || LOWER(t.text) || ' ' LIKE ?
             OR LOWER(h.term) = ?
             ORDER BY t.tdate DESC, t.ttime DESC;
             """

    c.execute(tweets, (keyword, hashtag))  # Made query injection safe
    tweetList = c.fetchall()
    return tweetList


"""
:param tid: tid of the tweet to display the stats of
:returns: Nothing
"""
def display_tweet_stats(tid):
    retweet_query = """
                SELECT COUNT(*)
                FROM retweets
                WHERE tid = ?
                GROUP BY tid;
                """
    c.execute(retweet_query, (tid,))
    retweets = c.fetchone()
    if retweets is None:
        retweets = 0
    else:
        retweets = retweets[0]
    reply_query = """
                SELECT COUNT(*)
                FROM tweets
                WHERE replyto_tid = ?
                GROUP BY tid;
                """
    c.execute(reply_query, (tid,))
    replies = c.fetchone()
    if replies is None:
        replies = 0
    else:
        replies = replies[0]
    print("Retweets: %d, Replies: %d" % (retweets, replies))


"""
:param usr: Currently signed in usr
:returns: Nothing
"""
def followers_wrapper(usr):
    page = 0
    results, page_count, item_count = list_followers(usr)
    page_type = 'f'
    item_count
    LISTING = True
    while LISTING:
        print(" Followers: \n")
        print(" usr_id | name | email")
        print('-' * 54)
        LISTING, page = display_page(page, item_count, page_count, results, page_type, usr, 1)


"""
:param usr: Currently signed in usr
:returns: Nothing
"""
def followed_wrapper(usr):
    f_tweets = followed_tweets(usr)
    if f_tweets:
        LISTING = True
        tweet_count = len(f_tweets)
        page_count = math.ceil(tweet_count/5)
        page_type = 's'
        page = 0
        while LISTING:
            print("\n To enter your dashboard please type: (R)eturn\n")
            print(" Followed tweets and retweets:")
            LISTING, page = display_page(page, tweet_count, page_count, f_tweets, page_type, usr, 2)


"""
:param usr: Currently signed in usr
:returns: Nothing
"""
def search_wrapper(usr_id):
    page = 0
    page_type = "s"
    SEARCHING = True
    while SEARCHING:
        print('=' * 50)
        print(" To search for tweets type:              (T)weets\
             \n To search for users type:               (U)sers\
             \n To return to the main menu please type: (R)eturn")
        print('=' * 50)

        inp = input("\n>").lower().strip()
        match inp:
            case 't' | 'tweets':
                c.execute("SELECT * FROM tweets")
                keyword = input("\n Please enter a keyword to search by\n>").lower().strip()
                tweet_list = select_tweet(keyword)
                tweet_count = len(tweet_list)
                page_count = math.ceil(tweet_count/5)
                SEARCHING_INNER = True
                while SEARCHING_INNER:
                    SEARCHING_INNER, page = display_page(page, tweet_count, page_count, tweet_list, page_type, usr_id, 0)

            case 'u' | 'users':
                keyword = input("\n Please enter a keyword to search by\n>").lower().strip()
                while not keyword.isalpha():
                    keyword = input("\n Please input a valid search term \n>").lower().strip()

                results, user_count, page_count = search_user(keyword)
                SEARCHING_INNER = True
                while SEARCHING_INNER:
                    SEARCHING_INNER, page = display_page(page, user_count, page_count, results, page_type, usr_id, 1)

            case 'r' | 'return':
                SEARCHING = False

"""
:param page:
:param item_count:
:param page_count:
:param results: A list containing the data to be displayed
:param page_type: If a search page, follow page, or more page is being displayed the data format changes. This accounts for the different types
:param usr: Currently signed in user
:param userFlag: A flag used to determine whether user or tweet data is being displayed
:returns: True if the user wishes to stay on the same menu, False if the user wishes to move the the previous menu
:returns page: Incremented or decremented or same page to be fed back into display_page()
"""
def display_page(page, item_count, page_count, results, page_type, usr, userFlag):
    item_range = 5  # default
    if ((page == page_count - 1) and (item_count % item_range != 0)):  # fixing index out of bounds for final page
        item_range = item_count % 5
    if results:  # checking if empty list
        match page_type:
            case 's':
                for i in range(page * 5, item_range + (page * 5)):
                    if len(results[i]) == 5:
                        print(" " + str(results[i][0]) + ": " + str(results[i][1]) + ", " + str(results[i][2]) + ", " + str(results[i][3]) + ", " + str(results[i][4]))
                    else:
                        print(" " + str(results[i][0]) + ": " + str(results[i][1]))
            case 'f' | 'm':
                for i in range(page * 5, item_range + (page * 5)):
                    print(" " + str(results[i][0]) + ": " + str(results[i][1]) + ", " + str(results[i][2]))
            case _:
                print("\n Invalid page type \n")
                return False, page
    else:
        print("\n No results\n")
        return False, page

    print("=" * 54)
    if (page != 0):
        print(" To go to the previous page type (B)ack")

    if ((page != page_count - 1) and (page_count != 0)):
        print(" To go to the next page type (N)ext")

    if (page_count not in (0, 1)):
        print(" To go to a specific page type the page number\
             \n Current page : " + str(page + 1) + "/" + str(page_count))

    if (userFlag == 1):
        print(" To select a user please type:               (Sel)ect\
             \n To follow a user please type:               (F)ollow")
    if (userFlag == 0):
        print(" To select a tweet for stats please type:    (Sel)ect\
             \n To reply to the tweet please type:          (Re)ply\
             \n To retweet the tweet please type:           (Ret)weet")
    if (page_type != 'l' and userFlag != 2):
        print(" To return to the previous menu please type: (R)eturn")

    print("=" * 54)
    page_iterate = input("\n>").lower().strip()
    if page_iterate.isdigit():  # cannot do this check in match case
        page = int(page_iterate) - 1
    else:
        match page_iterate:
            case 'sel' | 'select' | 'f' | 'follow':  # easier to do this and have it all display together.
                if (userFlag):
                    select_and_or_follow_user(usr, page_iterate)
                else:
                    tid = select_tid()
                    display_tweet_stats(tid)
            case 're' | 'reply':
                tid = select_tid()
                compose_tweet(usr, tid)
            case 'ret' | 'retweet':
                tid = select_tid()
                retweet(usr, tid)
            case 'b' | 'back':
                page -= 1
            case 'n' | 'next':
                page += 1
            case 'r' | 'return':
                if page_type != 'l':
                    return False, page
                else:
                    print(" Please input a valid selection")  # if we're on login dash and someone tries to troll
            case _:
                print(" Please input a valid selection")

    return True, page


if __name__ == '__main__':
    db = input(" Please input the file name of the db you wish to use\n>")
    connection = sqlite3.connect(db)
    c = connection.cursor()
    c.execute("PRAGMA foreign_keys = 1")
    RUNNING = True
    logged_in = (0, False)  # storing user id and current status of login
    # user interface
    first_time = True
    while RUNNING:
        if not logged_in[1]:
            first_time = True
            login_screen()  # put up login screen
            inp = input("\n>").lower().strip()

            match inp:
                case 'log' | 'login':
                    logged_in = login()

                case 'r' | 'register':
                    logged_in = register()  # user should be logged in if they register

                case 'q' | 'quit':
                    RUNNING = False

                case _:
                    print("Please input a valid selection\n")

        elif logged_in:
            if first_time:
                followed_wrapper(logged_in[0])
                first_time = False
            interface_screen()
            inp = input("\n>").lower().strip()
            match inp:
                case 's' | 'search':
                    search_wrapper(logged_in[0])

                case 'c' | 'compose':
                    compose_tweet(logged_in[0])

                case 'r' | 'retweet':
                    tid = select_tid()
                    retweet(logged_in[0], tid)

                case 'l' | 'list':
                    followers_wrapper(logged_in[0])
                case 'f' | 'following':
                    followed_wrapper(logged_in[0])
                case 'log' | 'logout':
                    logged_in = (logged_in[0], False)
                case _:
                    print(" Please input a valid selection")

    connection.close()
