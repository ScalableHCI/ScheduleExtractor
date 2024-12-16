import requests
from bs4 import BeautifulSoup

def fetch_and_clean_html(url):
    try:
        # Fetch the HTML content from the URL
        response = requests.get(url)
        response.raise_for_status()  # Check for request errors

        # Parse the HTML using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract the main table
        table = soup.find('table')
        if not table:
            raise ValueError("Table not found in the provided URL.")

        # Remove the top and bottom rows that might contain headers and footers.
        # Generally, these are rows like the document title or extra information.
        rows = table.find_all('tr')

        # Remove the first row (header or unnecessary info)
        if rows:
            rows[0].extract()

        # Remove the last row (footer or unnecessary info) if present
        if len(rows) > 1:
            rows[-1].extract()

        # Remove the leftmost column which holds only numbers
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if cells:
                cells[0].extract()

        # Wrap cleaned table in a div for embedding
        embedded_html = f"""
        <div class="embedded-table">
            {str(table)}
        </div>
        """

        # Optional: make it more readable by beautifying the output
        pretty_html = BeautifulSoup(embedded_html, 'html.parser').prettify()

        # Return the final HTML code to be embedded
        return pretty_html

    except requests.RequestException as e:
        print(f"An error occurred while fetching the URL: {e}")
    except ValueError as e:
        print(e)

# Specify the Google Spreadsheet URL
url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTxsgHgwYvaL4LOQxegbICkNCY0zdnDUtYf65eP47HgHcXqDlaGcexyVkLmJ9-0DgO30ILlymkp7YVF/pubhtml?gid=2136832740&single=true"

# Get the cleaned HTML code to embed
html_code = fetch_and_clean_html(url)

# Print the result
if html_code:
    print(html_code)

