from stravalib import Client

code = 'dc1eb65159b04e34d0529149c4db646b3d1e1a00' # e.g.
client = Client()
MY_STRAVA_CLIENT_SECRET='e3938884e234926885109ba4726449f7e036be1a '
access_token = client.exchange_code_for_token(client_id=47979,
                                              client_secret=MY_STRAVA_CLIENT_SECRET,
                                              code=code)
print(access_token)