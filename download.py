import requests
from bs4 import BeautifulSoup
import os

# Removes all characters that can not be in a file path
def clean(toClean):
    cleaned = toClean.replace(':', '')
    cleaned = cleaned.replace('/', '')
    cleaned = cleaned.replace('\\', '')
    cleaned = cleaned.replace('?', '')
    cleaned = cleaned.replace('<brk>', '')
    cleaned = cleaned.replace('"', '')
    cleaned = ' '.join(cleaned.split())
    return cleaned

# Gets a full url if only part is given
def getFullUrl(url):
    domain = 'http://www.marineband.marines.mil'
    if domain in url:
        return url
    else:
        return domain + url

# Asks the user what file location they would like to save the files in
# Folder must be on the same drive as the script being run
# Edit 'C:' to the drive you are running the script on if you need to
print('')
print('Enter the file path you would like to save your files in ')
saveLocation = input();
saveLocation = saveLocation.replace('C:', '')
saveLocation = saveLocation.replace('\\', '/')

currentPage = 'https://www.marineband.marines.mil/Audio-Resources/The-Complete-Marches-of-John-Philip-Sousa/'
mainPage = requests.get(currentPage).text
mainPage = BeautifulSoup(mainPage, 'html.parser')

# Loops through each volume
for volume in mainPage.find_all('tbody'):
    print(volume.find('strong').text)
    volumeTitle = volume.find('strong').text
    volumeTitle = clean(volumeTitle)
    
    # Loops through each song in a volume
    for song in volume.find_all('a'):
        songPage = requests.get(getFullUrl(song['href'])).text
        songPage = BeautifulSoup(songPage, 'html.parser')
        
        # Finds and names the .mp3 file on a song page
        mp3 = None
        score = None
        image = None
        mp3filetype = 'none'
        for link in songPage.find_all('a', href=True):
            linkcheck = link['href'].split('/')[-1].split('?')[0]
            if (linkcheck.endswith('.mp3')):
                mp3 = getFullUrl(link['href'])
                linkcheck = linkcheck.replace('%20', ' ')
                mp3filetype = linkcheck
                songnumber = mp3filetype.split('_', 1)
                if len(songnumber) > 1 and 72 < int(songnumber[0]) < 77 and songnumber[1] != 'Liberty_Loan.mp3':
                    mp3filetype = str(int(songnumber[0]) - 1) + '_' + songnumber[1]
                    
                break
                
        # Skips pages with no downloads
        if mp3filetype == 'none':
            print('no download available') 
            continue
   
        # Finds the pdf score and png file on a song page
        for link in songPage.find('tbody').find_all('a', href=True, attrs={'target': '_blank'}):
            linkcheck = link['href'].split('/')[-1].split('?')[0]
            print (linkcheck)
            if (linkcheck.endswith('.pdf')):
                if linkcheck.startswith(mp3filetype.split(' ')[0]) or linkcheck.startswith('Vol1_' + mp3filetype.split(' ')[0]) or linkcheck.startswith(mp3filetype.split('_')[0]):
                    score = getFullUrl(link['href'])
                    try:
                        image = getFullUrl(link.find('img')['src'])
                        break
                    except:
                        continue
        
        # Gets file and folder names
        songTitle = mp3filetype.rsplit('.', 1)[0].replace('_', ' ')
        savepath = saveLocation + '/' + volumeTitle + '/' + songTitle + '/'
        
        if not os.path.exists(savepath):
            os.makedirs(savepath)
            
        mp3fileSaveLocation = savepath + songTitle + '.mp3'
        scorefileSaveLocation = savepath + songTitle + '.pdf'
        imagefileSaveLocation = savepath + songTitle + '.png'
        
        # Downloads the files if they are not present in the folder
        try:
            with open(mp3fileSaveLocation) as f:
                print(songTitle, 'mp3 has already been downloaded')
                f.close()
        except FileNotFoundError:
            r2 = requests.get(mp3)
            with open(mp3fileSaveLocation, 'wb') as f:
                f.write(r2.content)
                f.close()
                
        try:
            with open(scorefileSaveLocation) as f:
                print(songTitle, 'score has already been downloaded')
                f.close()
        except FileNotFoundError:
            r2 = requests.get(score)
            with open(scorefileSaveLocation, 'wb') as f:
                f.write(r2.content)
                f.close()
                
        try:
            with open(imagefileSaveLocation) as f:
                print(songTitle, 'image has already been downloaded')
                f.close()
        except FileNotFoundError:
            r2 = requests.get(image)
            with open(imagefileSaveLocation, 'wb') as f:
                f.write(r2.content)
                f.close()
        
        print('Successfully downloaded ', songTitle)
    
print('Finished downloading all songs')
exit