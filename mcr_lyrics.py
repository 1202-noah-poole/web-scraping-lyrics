import requests
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from collections import Counter

#open web page
URL = "https://www.lyrics.com/artist.php?name=My-Chemical-Romance&aid=533805&o=1"
page = requests.get(URL)

#create soup object
soup = BeautifulSoup(page.content, "html.parser")

#gather content
content = soup.find(id = "content-main")

#gather the table
table = content.find_all("tr")
#print(len(table_elements))

#create empty dataframe for later storing
df = pd.DataFrame({"Song" : [], "Album" : [], "Duration" : [], "Song Link" : []})
#print(df.info())

for i in range(len(table) - 1):
    #locate elements of table (song, album, etc.)
    elements = table[i + 1].find_all("a")
    #duration:
    elements += table[i + 1].find(class_ = "tar qx")

    if (len(elements) < 3 ):
        continue

    #if there is not duaration, set to null value
    if (elements[2] == "\xa0"):
        elements[2] = None
    
    #fix link
    link = f"https://www.lyrics.com{elements[0]['href']}"

    #filter so that only main albums are kept (no live albums, singles, etc.)
    Albums = ['I Brought You My Bullets You Brought Me Your Love', 'Three Cheers for Sweet Revenge', 'The Black Parade',
            'Danger Days: The True Lives of the Fabulous Killjoys', 'Conventional Weapons, Vol. 1', 'Conventional Weapons, Vol. 2',
            'Conventional Weapons, Vol. 3', 'Conventional Weapons, Vol. 4', 'Conventional Weapons, Vol. 5']

    if (elements[1].text not in Albums):
        continue

    #append to df
    df.loc[len(df.index)] = (elements[0].text, elements[1].text, elements[2], link)

#print(df.head(20))
#print(df.info())

#data is still very messy, check each album and clean up:

#print(df.loc[df['Album'] == 'I Brought You My Bullets You Brought Me Your Love'])
#print(f"Length: {len(df.loc[df['Album'] == 'I Brought You My Bullets You Brought Me Your Love'])}") #all good

#print(df.loc[df['Album'] == 'Three Cheers for Sweet Revenge'])
#print(f"Length: {len(df.loc[df['Album'] == 'Three Cheers for Sweet Revenge'])}")
df.drop(df[df['Song'] == 'Helena (So Long & Goodnight)'].index, inplace=True) #fixed

#print(df.loc[df['Album'] == 'The Black Parade'])
#print(f"Length: {len(df.loc[df['Album'] == 'The Black Parade'])}")
df.drop(df[df['Song'] == 'Blood [*]'].index, inplace=True) #fixed

#print(df.loc[df['Album'] == 'Danger Days: The True Lives of the Fabulous Killjoys'])
#print(f"Length: {len(df.loc[df['Album'] == 'Danger Days: The True Lives of the Fabulous Killjoys'])}") #all good

#print(df.loc[df['Album'] == 'Conventional Weapons, Vol. 1'])
#almost good, need song lengths
df.loc[3]['Duration'] = "2:55"
df.loc[62]['Duration'] = "3:16"


#print(df.loc[df['Album'] == 'Conventional Weapons, Vol. 2'])
df.drop(df[df['Song'] == 'Gun'].index, inplace=True)  #fixed

#print(df.loc[df['Album'] == 'Conventional Weapons, Vol. 3']) #all good

#print(df.loc[df['Album'] == 'Conventional Weapons, Vol. 4'])
df.drop(df[df['Song'] == 'Make Room'].index, inplace=True)  #fixed

#print(df.loc[df['Album'] == 'Conventional Weapons, Vol. 5'])
#also needs song lengths
df.loc[5]['Duration'] = "4:17"
df.loc[48]['Duration'] = "3:27"

df.reset_index(inplace=True, drop = True)
print(df.info())

#update duration from object type to int type of seconds
for i in range(len(df.Duration)):
    L = df.Duration[i].split(':')
    count = (int(L[0]) * 60) + int(L[1])
    df.at[i, 'Duration'] = count
df.Duration = df.Duration.astype(int)

def get_song_lyrics(i):
    """Open the song url and collect the lyrics"""

    song_URL = df.loc[i]['Song Link']
    song_page = requests.get(song_URL)
    song_soup = BeautifulSoup(song_page.content, "html.parser")
    lyrics_raw = song_soup.find(id = "lyric-body-text")
    lyrics = lyrics_raw.text
    lyrics = lyrics.replace('\r', '')
    lyrics = lyrics.replace('\n', ' ')
    lyrics = lyrics.replace('  ', ' ')
    lyrics = lyrics.replace('(', '')
    lyrics = lyrics.replace(')', '')
    lyrics = lyrics.replace(',', '')
    lyrics = lyrics.lower()
    Lyrics = [x for x in lyrics.split()]
    return Lyrics

L = []
for i in range(len(df['Song'])):
    L += get_song_lyrics(i)

#purely surjective list of "boring words" to remove from common words
Boring_Words = ['the', 'and', 'i', 'to', 'a', 'it', 'your', 'we', 'all', 'if', 'this', 'so', 'for', 'my', 'in', 'of',
                "i'm", 'that', 'on', 'get', 'be', 'can', 'just', "don't", 'they', 'but', 'as', 'well', 'like', 'now', 'are', 
                'is', "'cause", "i'll", 'got', 'with', "you're", 'out', 'not', 'up', 'one', 'when', 'from', 'could', 
                'what', 'will', "we'll", 'la', "it's", 'oh', 'who', 'or', 'gonna', 'way', 'these', 'alright', 'have', 'every']
L = [x for x in L if x not in Boring_Words]

Most_Common = Counter(L).most_common(25)
print(Most_Common)

Words = []
Count = []

for x, y in Most_Common:
    Words.append(x)
    Count.append(y)

sns.barplot(x = Words, y = Count, palette = 'cividis')
plt.subplots_adjust(top = 0.92, bottom = 0.15)
#plt.grid(axis = 'y')
plt.xticks(rotation = 45, fontsize = 11)
plt.ylabel('Count', fontsize = 12)
plt.suptitle("'My Chemical Romance' Lyrics - 25 Most Common Words", fontweight = 'bold', fontsize = 12)
plt.title("Source: Lyrics.com", fontsize = 10)
plt.text(-4, -90, "Excludes (subjectively determined) 'boring' words, such as 'the', 'and', 'all', etc.", fontsize = 8, fontstyle = 'italic')
plt.show()