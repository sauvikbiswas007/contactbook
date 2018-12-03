from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from app.audit.views import get_new_audit
from app.contact.models import User, Contact
from app.contact.serializers import UserSerializer, UserDisplaySerializer, ContactSerializer, ContactDisplaySerializer
from common.util import is_missing_param_in_request, is_empty
from constants import constants
from constants.api_mandatory_field_lists import APIMandatoryFieldList


def is_valid_signup_request(data):
    if not data:
        return False, 'payload cannot be empty'

    mandatory_fields = APIMandatoryFieldList.get_mandatory_field_list(key='signup')
    is_missing_mandatory_details, message = is_missing_param_in_request(dict=data, key_list=mandatory_fields)
    if is_missing_mandatory_details:
        return False, message

    email = data['email']
    try:
        user = User.objects.get(email=email)
        if user.audit and not user.audit.is_deleted:
            return False, 'Given Email ID {0} is already registered and active'.format(email)
    except User.DoesNotExist:
        pass

    return True, None


def update_user(data, user_obj=None):
    user_serializer_data = {
        'email': user_obj.email if is_empty(dict=data, key='email') else data['email'],
        'phone': user_obj.phone if is_empty(dict=data, key='phone') else data['phone'],
    }

    if not user_obj:
        is_success, audit = get_new_audit()
        user_serializer_data['audit'] = audit.id
    else:
        user_obj.updated_at = timezone.now()
        user_obj.audit.save()
        user_serializer_data['audit'] = user_obj.audit.id

    if user_obj:
        user_serializer = UserSerializer(user_obj, data=user_serializer_data)
    else:
        user_serializer = UserSerializer(data=user_serializer_data)
    if user_serializer.is_valid():
        user = user_serializer.save()
        user.audit.created_by = user.id
        user.audit.updated_by = user.id
        user.audit.save()
        return True, user
    else:
        return False, user_serializer.errors


@api_view(['POST'])
@permission_classes((AllowAny,))
@authentication_classes([])
def add_user(request):
    """
    {
        "email": "emailone@yopmail.com",
        "phone": "3434343434"
    }
    """
    data = request.data
    is_valid_request, message = is_valid_signup_request(data=data)
    if not is_valid_request:
        return Response({'status': constants.API_ERROR, 'message': message}, status=status.HTTP_400_BAD_REQUEST)
    try:
        user = User.objects.get(email=data['email'])
        if user.audit and user.audit.is_deleted:
            user.audit.is_deleted = False
            user.audit.save()
        is_success = True
    except User.DoesNotExist:
        is_success, user = update_user(data=data)

    if not is_success:
        return Response({'status': constants.API_ERROR, 'message': user},
                        status=status.HTTP_400_BAD_REQUEST)

    return Response({'status': constants.API_SUCCESS, 'message': 'Successfully registered new user'},
                    status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes((AllowAny,))
@authentication_classes([])
def get_user_list(request):
    users = User.objects.filter(audit__is_deleted=False)
    if not len(users):
        return Response({'status': constants.API_SUCCESS, 'message': 'No Users found'},
                        status=status.HTTP_204_NO_CONTENT)
    return Response(
        {'status': constants.API_SUCCESS, 'message': 'Successfully retrieved {0} active users'.format(len(users)),
         'data': UserDisplaySerializer(users, many=True).data}, status=status.HTTP_200_OK)


def is_valid_user_details_request(user_id):
    if not user_id:
        return False, 'UserID cannot be empty'
    try:
        user = User.objects.get(pk=user_id)
        if user.audit and user.audit.is_deleted:
            return False, 'Given user is not active'
    except User.DoesNotExist:
        return False, 'No User found with given ID - {0}'.format(user_id)

    return True, None


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((AllowAny,))
@authentication_classes([])
def user_details(request, user_id):
    is_valid_request, message = is_valid_user_details_request(user_id=user_id)
    if not is_valid_request:
        return Response({'status': constants.API_ERROR, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    user = User.objects.get(pk=user_id)

    if request.method == 'GET':
        return Response({'status': constants.API_SUCCESS, 'message': 'Successfully retrieved details of given user',
                         'data': UserDisplaySerializer(user).data}, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        user.audit.is_deleted = True
        user.audit.save()
        return Response({'status': constants.API_SUCCESS, 'message': 'Successfully deleted given user'},
                        status=status.HTTP_200_OK)

    else:
        data = request.data
        is_success, user = update_user(user_obj=user, data=data)
        if not is_success:
            return Response({'status': constants.API_ERROR, 'message': user}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'status': constants.API_SUCCESS, 'message': 'Successfully updated given user'},
                        status=status.HTTP_200_OK)


def is_valid_add_contact_list_request(data):
    if not data:
        return False, 'payload cannot be empty'

    mandatory_fields = APIMandatoryFieldList.get_mandatory_field_list(key='add_contact_list')
    is_missing_mandatory_details, message = is_missing_param_in_request(dict=data, key_list=mandatory_fields)
    if is_missing_mandatory_details:
        return False, message

    owner = data['owner']
    try:
        user = User.objects.get(pk=owner)
        if user.audit and user.audit.is_deleted:
            return False, 'Given Owner is not active'
    except User.DoesNotExist:
        return False, 'No User found with given Owner - {0}'.format(owner)

    contact_list = data['contact_list']
    print('contact_list = ', contact_list)
    if type(contact_list) is not list:
        return False, 'contact_list must be of type list, received type {0} instead'.format(type(contact_list))

    for curr_contact in contact_list:
        print('curr_contact = ', curr_contact)
        mandatory_fields = APIMandatoryFieldList.get_mandatory_field_list(key='signup')
        is_missing_mandatory_details, message = is_missing_param_in_request(dict=curr_contact,
                                                                            key_list=mandatory_fields)
        if is_missing_mandatory_details:
            return False, message

        email = curr_contact['email']
        try:
            contact = User.objects.get(email=email)
            if contact.audit and contact.audit.is_deleted:
                return False, 'Given Contact with email {0} is not active'.format(email)
        except User.DoesNotExist:
            pass

    return True, None


def update_contact_list_details(owner, contact_list):
    try:
        contact = Contact.objects.get(owner=owner)
        for curr_contact in contact_list:
            email = curr_contact['email']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                is_success, user = update_user(data=curr_contact)
                if not is_success:
                    return False, user
            if not user in contact.contact_list.all():
                contact.contact_list.add(user)
                contact.save()
    except Exception as e:
        return False, str(e)

    return True, None


@api_view(['POST', 'GET'])
def contact_list(request):
    """
    {
        "owner": 4,
        "contact_list": [{
                "email": "emailtwo@yopmail.com",
                "phone": "1111111111"
            },
            {
                "email": "emailthree@yopmail.com",
                "phone": "2222222222"
            },
            {
                "email": "emailfour@yopmail.com",
                "phone": "3333333333"
            }
        ]
    }
    """

    if request.method == 'GET':
        contacts = Contact.objects.filter(audit__is_deleted=False)
        if not len(contacts):
            return Response({'status': constants.API_SUCCESS, 'message': 'No Contacts found'},
                            status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'status': constants.API_SUCCESS, 'message': 'Successfully retrieved {0} contacts'.format(len(contacts)),
             'data': ContactDisplaySerializer(contacts, many=True).data}, status=status.HTTP_200_OK)

    else:
        data = request.data
        is_valid_request, message = is_valid_add_contact_list_request(data=data)
        if not is_valid_request:
            return Response({'status': constants.API_ERROR, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

        owner = User.objects.get(pk=data['owner'])
        try:
            contact = Contact.objects.get(owner=owner)
            if contact.audit:
                if contact.audit.is_deleted:
                    contact.audit.is_deleted = False
                contact.audit.updated_at = timezone.now()
                contact.audit.save()
            else:
                is_success, audit = get_new_audit(created_by=owner.id, updated_by=owner.id)
                contact.audit = audit
                contact.audit.save()
                contact.save()
        except Contact.DoesNotExist:
            is_success, audit = get_new_audit(created_by=owner.id, updated_by=owner.id)
            if not is_success:
                return Response({'status': constants.API_ERROR, 'message': audit}, status=status.HTTP_400_BAD_REQUEST)
            contact_serializer_data = {
                'owner': owner.id,
                'audit': audit.id
            }
            contact_serializer = ContactSerializer(data=contact_serializer_data)
            if not contact_serializer.is_valid():
                return Response({'status': constants.API_ERROR, 'message': contact_serializer.errors},
                                status=status.HTTP_400_BAD_REQUEST)

            contact = contact_serializer.save()

        contact_list = data['contact_list']
        is_success, message = update_contact_list_details(owner=owner, contact_list=contact_list)
        if not is_success:
            return Response({'status': constants.API_ERROR, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'status': constants.API_SUCCESS, 'message': 'Successfully updated contact list'},
                        status=status.HTTP_200_OK)


def is_valid_search_contact_requets(data):
    if not data:
        return False, 'payload cannot be empty'

    mandatory_fields = APIMandatoryFieldList.get_mandatory_field_list(key='search_contact')
    is_missing_mandatory_details, message = is_missing_param_in_request(dict=data, key_list=mandatory_fields)
    if is_missing_mandatory_details:
        return False, message

    owner = data['owner']
    try:
        user = User.objects.get(pk=owner)
        if user.audit and user.audit.is_deleted:
            return False, 'Given owner is no more active'
        try:
            contact = Contact.objects.get(owner=user)
            if (contact.audit and contact.audit.is_deleted) or not len(contact.contact_list.all()):
                return False, 'No Contacts found for given Owner - {0}'.format(owner)
        except Contact.DoesNotExist:
            return False, 'No Contacts found for given Owner - {0}'.format(owner)
    except User.DoesNotExist:
        return False, 'No User found with given ownerID - {0}'.format(owner)

    return True, None


@api_view(['POST'])
def search_contact(request):
    data = request.data
    is_valid_request, message = is_valid_search_contact_requets(data=data)
    if not is_valid_request:
        return Response({'status': constants.API_ERROR, 'message': message}, status=status.HTTP_400_BAD_REQUEST)

    contact = Contact.objects.get(owner_id=data['owner'])
    search_key = data['search_key']
    email_query = Q(email__icontains=search_key)
    phone_query = Q(phone__icontains=search_key)
    users = contact.contact_list.filter(email_query | phone_query)
    if not len(users):
        return Response({'status': constants.API_SUCCESS, 'message': 'No contacts found with given search key'},
                        status=status.HTTP_204_NO_CONTENT)
    return Response({'status': constants.API_SUCCESS,
                     'message': 'Successfully found {0} contacts matching given search key'.format(len(users)),
                     'data': UserDisplaySerializer(users, many=True).data}, status=status.HTTP_200_OK)
