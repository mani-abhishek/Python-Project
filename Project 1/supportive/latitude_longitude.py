import geocoder

latitude = geocoder.ip('me').latlng[0]
longitude = geocoder.ip('me').latlng[1]

print(latitude)
print(longitude)

