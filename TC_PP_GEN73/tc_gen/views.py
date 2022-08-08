from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

#terms-genrattor imports -mariam & jude
from .models import Company, Template
from .forms import WebsiteForm
import re #for regex
import pdfkit
from pdfkit.api import  configuration #PDF library

# Create your views here.

#creating views for generate form, terms generate, download

def termsform(request):
    # Check if POST request is made
    if request.method == 'POST':
        # Save the values to the form
        website_form = WebsiteForm(request.POST)
        # Retrieve the values from the form and save them to variables
        company_name = request.POST['company_name']
        company_website_name = request.POST['company_website_name']
        company_website_url = request.POST['company_website_url']
        country = request.POST['country']
        state = request.POST['state']
        company_email_address = request.POST['company_email_address']

        # Insert the values to a model instance and save it to the database
        new_company = Company(
            company_name = company_name,
            company_website_name = company_website_name,
            company_website_url = company_website_url,
            country = country,
            state = state,
            company_email_address = company_email_address
        )

        new_company.save()

        # Redirect to another page after saving the model
        return redirect('/generator')

    # Else initialize an empty form
    website_form = WebsiteForm()
    # Pass the data to the context variable
    context = {
        'website_form': website_form
    }
    # Render the results to a HTML page
    return render(request, 'tc_gen/index.html', context)

# Function to generate terms and conditions
def generate_terms(request):
    # Initialize an id
    id = 0
    # Loop through the companies and assign the id to the id of the last one
    for company in Company.objects.all():
        id = company.id
    
    # Check if a POST request is made
    if request.method == 'POST':
        # Get the company name from the POST request and save it to a variable
        company = Company.objects.filter(company_name = request.POST['company_name'])
        # Get the slug value from the company name and convert to lowercase and remove any spaces
        slug = request.POST['company_name'].lower()
        slug = re.sub('[^A-Za-z0-9]', '', slug)

        # Insert the values to a model instance and save it to the database
        new_template = Template(
            company = company,
            slug = slug
        )
        
        new_template.save()
    # Pass the data to the context variable
    context = {
        'company': Company.objects.filter(id=id),
        'saved_terms': Template.objects.all()
    }
    # Render the results to a HTML page
    return render(request, 'tc_gen/terms.html', context)
# Function to view saves terms and conditions
def view_saved_terms(request, slug):
    # Save all the previously saved terms and condions to the context variable
    context = {
        'saved_terms': Template.objects.all()
    }
    # Return the generate terms function
    return generate_terms(request)

# Function to downoad A generated terms and conditions as PDF
def download_pdf(request, company_name):
    # Get a company by its name
    selected_company = Company.objects.get(company_name=company_name)

    # Read the template file and push each line to a list
    lines = []
    with open('src/terms_sample.txt') as f:
        lines = f.readlines()
    # Initialize a count variable and a list
    count = 0
    new_lines = []
    # Initialize the final string
    final_string = ''
    # Loop through the lines in the template file and replace the placeholders with variables
    for line in lines:
        if '{{ company.company_website_name }}' in line:
            line = re.sub('{{ company.company_website_name }}', selected_company.company_website_name, line, flags=re.IGNORECASE)
        
        if '{{ company.company_name }}' in line:
            line = re.sub('{{ company.company_name }}', selected_company.company_name, line, flags=re.IGNORECASE)

        if '{{ company.company_website_url }}' in line:
            line = re.sub('{{ company.company_website_url }}', selected_company.company_website_url, line, flags=re.IGNORECASE)

        if '{{ company.company_email_address }}' in line:
            line = re.sub('{{ company.company_email_address }}', selected_company.company_email_address, line, flags=re.IGNORECASE)
        # Append the edited lines to the initialized list and increment the count
        new_lines.append(line)
        count += 1
    # Append the initialized list to the final_string variable
    for line in new_lines:
        final_string += line
    # Set options for the PDF file
    options = {
        'page-size': 'Letter',
        'margin-top': '0.75in',
        'margin-right': '0.75in',
        'margin-bottom': '0.75in',
        'margin-left': '0.75in',
        'encoding': "UTF-8",
        'no-outline': None
        }

        #set configuration for wkhtmltopdf
    path_wkhtmltopdf = "C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
    config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)



    # Use False instead of output path to save pdf to a variable
    # Remove any special characters from the company name and save it to the filename
    filename = re.sub('[!,*)@#%(&$_?.^]', '', f'{selected_company.company_name}')
    # Generate a PDF from the final_string variable
    pdf = pdfkit.from_string(final_string,  options=options, configuration= config)
    # Save the generated PDF to the filename and download it
    response = HttpResponse(pdf,content_type='application/pdf')
    response['Content-Disposition'] = 'filename='f'{filename}.pdf'

    return response

#creating the view for the terms and conditions preview
def tc_preview(request):

    #DUMMY DATA
    context = {
        'name': 'Ayodele',
        'email': 'ayodelekadiri.ak@gmail.com',
        'site': 'thehandsomeguys.com'
    }

    return render(request, 'tc_gen/tc_preview.html', context)

#view for the document you want to download
def tc_download(request):

    #DUMMY DATA
    context = {
        'name': 'Ayodele',
        'email': 'ayodelekadiri.ak@gmail.com',
        'site': 'thehandsomeguys.com'
    }

    #path of the template you want to download
    template_path = 'tc_gen/tc_download_ready.html'

    response = HttpResponse(content_type = 'application/pdf')
    response['Content-Disposition'] = 'filename="Terms_and_Conditions.pdf"'

    template = get_template(template_path)
    html = template.render(context)

    #create pdf
    pisa_status = pisa.CreatePDF(html, dest=response)

    if pisa_status.err:
        return HttpResponse('Errors occured while generating the pdf.')

    return response

