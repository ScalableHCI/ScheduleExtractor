import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

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

        # Remove the top and bottom rows (headers, footers, etc.)
        rows = table.find_all('tr')
        if rows:
            rows[0].extract()  # Remove first row
        if len(rows) > 1:
            rows[-1].extract()  # Remove last row

        # Remove the leftmost column which often holds row numbers
        for row in table.find_all('tr'):
            cells = row.find_all(['td', 'th'])
            if cells:
                cells[0].extract()

        # (Optional) Remove any existing inline style attributes from cells
        for cell in table.find_all(['td', 'th']):
            if cell.has_attr('style'):
                del cell['style']

        # Make the *new* first row bold by turning its <td> cells into <th> cells
        new_rows = table.find_all('tr')
        if new_rows:  # If there's at least one row left
            first_row_cells = new_rows[0].find_all('td')
            for cell in first_row_cells:
                cell.name = 'th'  # Changing <td> to <th> makes them bold by default

        # ----------------------------------------------------------------------
        #  Clean up links of the form: https://www.google.com/url?q=<REAL_URL>
        # ----------------------------------------------------------------------
        for link in table.find_all('a'):
            href = link.get('href', '')
            if href.startswith("https://www.google.com/url?q="):
                # Extract actual URL from 'q' parameter
                parsed = urlparse(href)
                qs = parse_qs(parsed.query)
                real_url = qs.get('q', [''])[0]  # get first item or empty string
                if real_url:
                    # Replace the href with the real URL
                    link['href'] = real_url

        # Create a style block to enforce uniform table cells
        # and also enlarge <th> cells
        style_block = """
        <style>
            table {
                border: 1px solid #000;
                border-collapse: collapse;
                table-layout: fixed; /* Enforces your specified column widths */
            }
            th, td {
                width: 110px;       /* Adjust for most columns */
                height: 35px;
                text-align: left;
                vertical-align: top;
                overflow: hidden;
            }
            th:first-child, td:first-child {
                width: 20px;       /* smaller width for leftmost column */
            }
            /* Make all <th> cells bigger (you can tweak the values below) */
            th {
                font-size: 13px;   /* Increase the font size */
                height: 20px;
            }
            .waffle tr {
                background-color: #fff !important;
            }
        </style>
        """

        # Wrap cleaned table in a div for embedding + include the style block
        embedded_html = f"""
        <div class="embedded-table" style="font-size: 10px;">
            {style_block}
            {str(table)}
        </div>
        """

        # Make it more readable by beautifying the output
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

