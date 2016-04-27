from django.contrib.auth import logout as auth_logout, login
from django.shortcuts import redirect
from recipes.models import RecipeUser
from utils import *

def save_profile(backend, user, response, *args, **kwargs):
    data = {}
    if backend.name == "google-oauth2":
        data['profilePic'] = response.get('image', {}).get('url', None)
        data['name'] = response.get('displayName', None)
        data['email'] = response.get('emails', [{}])[0].get('value', None)
        data['googleUser'] = user
        recipeUser = RecipeUser.objects.filter(googleUser = user)
    elif backend.name == 'facebook':
        if 'id' in response:
            data['profilePic'] = 'http://graph.facebook.com/' + response['id'] + '/picture?type=square'
        data['name'] = response.get('name', None)
        data['email'] = response.get('email', None)
        data['facebookUser'] = user
        recipeUser = RecipeUser.objects.filter(facebookUser = user)

    if not recipeUser.exists():
        userByEmail = RecipeUser.objects.filter(email = data['email'])
        if userByEmail.exists():
            logging.info('email exists, joining account')
            recipeUser = userByEmail
        else:
            RecipeUser.objects.create(
                googleUser = data.get('googleUser', None),
                facebookUser = data.get('facebookUser', None),
                profilePic = data.get('profilePic', None),
                name = data.get('name', None),
                email = data.get('email', None)
            )
            return;
    recipeUser = recipeUser[0]
    changed = False
    for attr in data:
        if not getattr(recipeUser, attr) and data[attr]:
            setattr(recipeUser, attr, data[attr])
            changed = True
    if changed:
        recipeUser.save()

def logout(request):
    """Logs out user"""
    auth_logout(request)
    return redirect('/')



api_version = "v1.0"
app_id = ''
app_secret = '';
me_endpoint_base_url = 'https://graph.accountkit.com/v1.0/me';
token_exchange_base_url = 'https://graph.accountkit.com/v1.0/access_token';
import hmac
import hashlib
import base64

def genAppSecretProof(app_secret, access_token):
    h = hmac.new (
        app_secret.encode('utf-8'),
        msg=access_token.encode('utf-8'),
        digestmod=hashlib.sha256
    )
    return h.hexdigest()

def accountkit_login(request):
    app_access_token = '|'.join(['AA', app_id, app_secret])
    print app_access_token
    params = \
        'grant_type=' + 'authorization_code' + \
        '&code=' + request.POST.get('code') + \
        '&access_token=' + app_access_token

    token_exchange_url = token_exchange_base_url + '?' + params;
    print token_exchange_url
    response = requests.get(token_exchange_url)
    data = response.json()
    # Request.get({url: token_exchange_url, json: true}, function(err, resp, respBody) {
    #   var view = {
    #     user_access_token: respBody.access_token,
    #     expires_at: respBody.expires_at,
    #     user_id: respBody.id,
    #   };
    #
    #   // get account details at /me endpoint
    print data

    appsecret_proof = genAppSecretProof('', data['access_token'])
    me_endpoint_url = me_endpoint_base_url + '?access_token=' + data['access_token'] + '&appsecret_proof=' + appsecret_proof;
    me_endpoint_url = me_endpoint_base_url + '?access_token=' + data['access_token'];
    print me_endpoint_url
    response = requests.get(me_endpoint_url)
    print response.text
    #   Request.get({url: me_endpoint_url, json:true }, function(err, resp, respBody) {
    #     // send login_success.html
    #     if (respBody.phone) {
    #       view.phone_num = respBody.phone.number;
    #     } else if (respBody.email) {
    #       view.email_addr = respBody.email.address;
    #     }
    #     var html = Mustache.to_html(loadLoginSuccess(), view);
    #     response.send(html);
    #   });
    # });
    return render(request, 'index.html')
