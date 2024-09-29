import requests
from django.conf.global_settings import EMAIL_HOST_USER
from django.contrib.auth import login, update_session_auth_hash, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, SetPasswordForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.views.decorators.cache import never_cache

from micro_ecommerce import settings
from usuario.forms import CrearUsuarioFormulario, PerfilUsuarioFormulario
from django.core.mail import EmailMessage,send_mail

from usuario.models import Rol, Usuario

from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import CrearUsuarioFormulario
from .token import account_activation_token
from django.contrib.auth.models import User
import requests
from django.conf import settings
from django.template.loader import render_to_string


# Create your views here.


def crear_usuario(request):
    if request.method == 'POST':
        formulario = CrearUsuarioFormulario(request.POST)

        # secret_key = settings.RECAPTCHA_SECRET_KEY
        #
        # # Captcha verification
        # data = {
        #     'response': request.POST.get('g-recaptcha-response'),
        #     'secret': secret_key
        # }
        # resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        # result_json = resp.json()
        #
        # if not result_json.get('success'):
        #     return render(request, 'usuario/create.html', {'form': formulario})

        if formulario.is_valid():
            user = formulario.save(commit=False)

            rol_cliente = Rol.objects.get(nombre='cliente')  # Asegúrate de que este rol exista

            user.is_active = False  # Desactivar el usuario hasta que verifique su correo
            user.save()
            nuevo_usuario = Usuario(user=user, rol=rol_cliente)
            nuevo_usuario.save()

            # Enviar correo de verificación
            subject = 'Activa tu cuenta'
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))  # Codifica el ID del usuario
            context = {
                'user': user,
                'domain': request.get_host(),
                'uidb64': uidb64,  # Cambia aquí a uidb64
                'token': account_activation_token.make_token(user),
            }
            html_message = render_to_string('usuario/activation_email.html', context)

            send_mail(
                subject=subject,
                message="Activar cuenta",
                from_email=EMAIL_HOST_USER,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, 'Te hemos enviado un correo de verificación. Por favor, verifica tu cuenta.')
            return redirect('usuario:login')  # Redirige al usuario a la página de inicio de sesión
    else:
        formulario = CrearUsuarioFormulario()

    for field in formulario.fields.values():
        field.widget.attrs.update({
            'class': 'form-control',
            'placeholder': field.label
        })

    return render(request, 'usuario/create.html', {'form': formulario})


def iniciar_sesion(request):
    if request.user.is_authenticated:
        return redirect('products:list')

    formulario = AuthenticationForm()
    if request.method == 'POST':

        # secret_key = settings.RECAPTCHA_SECRET_KEY
        #
        # # captcha verification
        # data = {
        #     'response': request.POST.get('g-recaptcha-response'),
        #     'secret': secret_key
        # }
        # resp = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        # result_json = resp.json()
        #
        #
        # if not result_json.get('success'):
        #     return render(request, 'usuario/login.html', {'formulario': formulario})


        formulario = AuthenticationForm(request, data=request.POST)
        if formulario.is_valid():
            usuario = formulario.get_user()
            login(request, usuario)
            if usuario.usuario.rol.nombre == 'admin':
                return redirect('/administrador/')
            else:
                return redirect('products:list')  # Redirige al usuario a la página de inicio
        else:
            messages.error(request, 'El usuario o la contraseña es incorrecta')
    else:
        formulario = AuthenticationForm()

    for field in formulario.fields.values():
        field.widget.attrs.update({
            'class': 'form-control',
            'placeholder': field.label
        })


    return render(request, 'usuario/login.html', {'formulario': formulario})





@login_required
def editar_perfil(request):
    if request.method == 'POST':
        formulario = PerfilUsuarioFormulario(request.POST, instance=request.user)
        if formulario.is_valid():
            formulario.save()
            return redirect('products:list')  # Redirige al usuario a la página de perfil
    else:
        formulario = PerfilUsuarioFormulario(instance=request.user)

        for field in formulario.fields.values():
            field.widget.attrs.update({
                'placeholder': field.label
            })

    print(formulario)
    return render(request, 'usuario/update_user.html', {'form': formulario})


@login_required

def cerrar_sesion(request):
    logout(request)
    return redirect('usuario:login')





@login_required
def cambiar_contrasena(request):
    if request.method == 'POST':
        formulario = PasswordChangeForm(user=request.user, data=request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            update_session_auth_hash(request, usuario)  # Actualiza la sesión del usuario para evitar que se cierre la sesión
            messages.success(request, 'Tu contraseña ha sido actualizada.')
            return redirect('listar_clasificaciones')  # Redirige al usuario a la página de perfil
    else:
        formulario = PasswordChangeForm(user=request.user)

        for field in formulario.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })
    return render(request, 'usuario/change.html', {'formulario': formulario})



@login_required
def eliminar_usuario(request):
    # Obtén el usuario que desea eliminar
    usuario = get_object_or_404(User, id=request.user.id)

    usuario.delete()

        # Redirige a una página de éxito o cualquier otra acción que desees realizar después de eliminar al usuario
    return redirect('usuario:login')



class MyPasswordChangeView(PasswordChangeView):
    template_name = 'usuario/change_password.html'
    form_class = PasswordChangeForm
    success_url = '/usuario/pasword_change'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields['old_password'].widget.attrs['class'] = 'form-control'
        form.fields['old_password'].widget.attrs['style'] = 'background-color: rgba(255,255,255,0)'
        form.fields['new_password1'].widget.attrs['class'] = 'form-control'
        form.fields['new_password1'].widget.attrs['style'] = 'background-color: rgba(255,255,255,0)'
        form.fields['new_password2'].widget.attrs['class'] = 'form-control'
        form.fields['new_password2'].widget.attrs['style'] = 'background-color: rgba(255,255,255,0)'
        return form



@login_required()
def password_change_done(request):
    return render(request, 'usuario/password_change_done.html')


from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes


def activate(request, uidb64, token):
    User = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('products:list')  # Redirige a la página de inicio o a donde quieras
    else:
        return render(request, 'usuario/activation_invalid.html')  # Plantilla para un enlace inválido