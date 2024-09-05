import requests, os, json, time
from bs4 import BeautifulSoup

DB_ROUTE = "./databooks.json"
MAIN_URL = "https://infolibros.org/libros-pdf-gratis/"

class Booker():
    
    def __init__(self, book_name = None, category_book = None) -> None:
        self.book_name = book_name
        self.book_category = category_book
    def find_database(self):
        
        if not self.check_database():
            return False
        
        loaded_data = json.loads(open(DB_ROUTE, 'r').read())
        
        if self.book_name == None and self.book_category != None:
            filtered_data = list(filter(lambda x: self.book_category.lower() in x["category"].lower(),loaded_data))
            print(filtered_data)
        elif self.book_name != None and self.book_category == None:
            filtered_data = list(filter(lambda x: self.book_name.lower() in x["name"].lower(),loaded_data))
            print(filtered_data)
        
    def update_database(self):
        
        db_file = open(DB_ROUTE, 'w')
        
        temp_data = []
        
        initial_request = requests.get(MAIN_URL)
        
        soup = BeautifulSoup(initial_request.text, 'html.parser')
        
        table_container = soup.find('table', {'class': 'has-fixed-layout'})
        
        main_books = table_container.find_all('tr')
        
        for first_books in main_books:
            book_name = first_books.find('strong').text
            book_url = first_books.find('a')['href']
            temp_data.append({"name": book_name, "url": book_url, "category": "most_wanted"})

        categories_link = soup.find_all('p', {'class': 'libros_interlink'})
        categories_link = [ {"url": x.find('a')['href'], "category_name": x.find('a')['href'].split('/')[-2]} for x in categories_link]
        
        len_category = len(categories_link)
        
        time_start = time.time()
        time_waiting = 'N'
        for i,category in enumerate(categories_link):

            print(f'\rCATEGORY: {i + 1}/{len_category} || Aprox. {time_waiting}min', end='')
            r = requests.get(category['url'])
            soup2 = BeautifulSoup(r.text, 'html.parser')
            
            books_found = soup2.find_all('div', {'class': 'Libros_Container'})
            
            for book in books_found:
                book_name = book.find('p', {'class': 'Libros_Titulo'}).text
                book_url = book.find('a', {'class': 'Libros_Boton_Dos'})['href']
                book_category = category['category_name']
                temp_data.append({"name": book_name, "url": book_url, "category": book_category})
                
            if i == 9:
                time_stop = time.time()
                time_lapsed = (time_start - time_stop) * -1
                time_waiting = int(((len_category * time_lapsed / 10) - time_lapsed) / 60)
                time_start = time.time()
            if i > 10:
                time_stop = time.time()
                lapsed_temp = (time_start - time_stop) * -1
                
                if lapsed_temp > 60:
                    time_waiting -= 1
                    time_start = time.time()    
                
        
        db_file.write(json.dumps(temp_data))
        db_file.close()
        print('\n\nThe database has been updated')
        
    def check_database(self):
        return True if os.path.exists(DB_ROUTE) else False
        

myBookInvoker = Booker(book_name='orgullo y prejuicio')

db_exists = myBookInvoker.update_database()

# myBookInvoker.find_database()
