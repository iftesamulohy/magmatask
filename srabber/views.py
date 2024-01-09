from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
from django.views.generic.base import TemplateView
from django.shortcuts import redirect, render
class ColorInfo:
    def __init__(self, available_colors, selected_color):
        self.available_colors = available_colors
        self.selected_color = selected_color

class Index(TemplateView):
    template_name = "srabber/index.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Check if 'title' is available in the session (set during the POST request)
        # Check if 'title' is present in the query parameters
        title = self.request.GET.get('title')
        if title:
            context['title'] = title
        return context
    def post(self, request, *args, **kwargs):
        context = {}
        url = request.POST['url']
        print(url)
        # Make a request to the URL
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the HTML content using Beautiful Soup
            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract data from the HTML (replace this with your specific logic)
            title = soup.title.text
            price = soup.select('.x-price-primary .ux-textspans')[0].text
            # Save the title in the session to access it in get_context_data
            # Extract availability information
            availability_div = soup.find('div', class_='d-quantity__availability')
            if availability_div:
                availability_text = ' / '.join(span.get_text(strip=True) for span in availability_div.find_all('span'))
            else:
                availability_text = 'Availability information not found on the page'
            # Extract color information
            color_select_box = soup.find('select', {'class': 'x-msku__select-box'})
            if color_select_box:
                color_options = color_select_box.find_all('option')
                colors = [option.text.strip() for option in color_options if not option.has_attr('disabled')]
                available_colors = [option.text.strip() for option in color_options if not option.has_attr('disabled')]
                selected_color = [option.text.strip() for option in color_options if option.has_attr('selected')]
                color_info = f'Available Colors: {", ".join(colors)}\nSelected Color: {", ".join(selected_color)}'
                color_info = ColorInfo(available_colors, selected_color)
            else:
                color_info = None
            
            print(price)
            context['title'] = title
            context['price'] = price
            context['color_info'] = color_info
            context['availability_text'] = availability_text

        return self.render_to_response(context)


































##soub scrabber
def scrape_and_save(request):
    # URL to scrape
    url = "https://www.ebay.com/itm/403448574550?_trkparms=pageci%3Acd1ed79b-ad30-11ee-b2c6-360adef080bd%7Cparentrq%3Ae2e2c0dc18c0ac68ed6e05dbfffed11c%7Ciid%3A1"

    # Make a request to the URL
    response = requests.get(url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the HTML content using Beautiful Soup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Extract data from the HTML (replace this with your specific logic)
        title = soup.title.text
        paragraphs = soup.find_all('span', {'class': 'ux-textspans'})

        # Try to find the price within specific HTML elements on the Daraz page
        price_element = soup.find('span', {'class': 'ux-textspans'})
        quantity_spans = soup.select('.x-price-primary .ux-textspans')

        if price_element:
            price = price_element.text.strip()
        else:
            price = 'Price not found on the page'
        for span in quantity_spans:
            print(span.text)

        # Extract color information from the provided HTML snippet
        color_select_box = soup.find('select', {'class': 'x-msku__select-box'})
        if color_select_box:
            color_options = color_select_box.find_all('option')
            colors = [option.text.strip() for option in color_options if not option.has_attr('disabled')]
            selected_color = [option.text.strip() for option in color_options if option.has_attr('selected')]

            color_info = f'Available Colors: {", ".join(colors)}\nSelected Color: {", ".join(selected_color)}'
        else:
            color_info = 'Color information not found on the page'

        # Create a text content string
        content = f'Title: {title}\n\nPrice: {price}\n\n{color_info}\n\nParagraphs:\n'
        content += '\n'.join([f'- {paragraph.text}' for paragraph in paragraphs])
        content += '\n'.join([f'- {paragraph.text}' for paragraph in quantity_spans])

        # Write the extracted data to a text file
        with open('extracted_data.txt', 'w', encoding='utf-8') as file:
            file.write(content)

        # Return a text response
        return HttpResponse(content, content_type='text/plain')
    else:
        # Handle the case when the request fails
        return HttpResponse('Failed to fetch data from the website', status=500, content_type='text/plain')
