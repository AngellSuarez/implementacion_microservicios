from django.core.mail import send_mail
from django.conf import settings

def enviar_correo_recuperacion(destinatario, asunto, codigo):
    """
    Envía un correo con un código de recuperación usando HTML personalizado.
    """
    mensaje_texto = f'Tu código de recuperación es: {codigo}'

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #fff3f8; border-radius: 10px; border: 1px solid #f8c6e0;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/736x/ab/dd/f1/abddf13749e496af6b9bfc5f5bec55e4.jpg" alt="Recuperación de contraseña" style="max-width: 150px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #333; text-align: center;">🔐 Recuperación de contraseña</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hemos recibido una solicitud para restablecer tu contraseña en <strong>Mi App</strong>.
        </p>
        <div style="text-align: center; margin: 30px 0;">
            <p style="font-size: 18px; color: #333;">Tu código es:</p>
            <p style="font-size: 32px; font-weight: bold; color: #4A154B; letter-spacing: 2px;">{codigo}</p>
        </div>
        <p style="font-size: 14px; color: #777; text-align: center;">
            Este código expirará en 10 minutos. Si no solicitaste este código, puedes ignorar este correo.
        </p>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False

def enviar_correo_registro(destinatario, nombre_usuario):
    """
    Envía un correo de bienvenida tras el registro del cliente.
    """
    asunto = "Bienvenido(a) a CandyNails 💅"
    mensaje_texto = f"Hola {nombre_usuario}, gracias por registrarte en CandyNails. 🎉"

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #fff3f8; border-radius: 10px; border: 1px solid #f8c6e0;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/736x/ab/dd/f1/abddf13749e496af6b9bfc5f5bec55e4.jpg" alt="Bienvenida" style="max-width: 120px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #d63384; text-align: center;">🎉 ¡Bienvenido(a) a CandyNails!</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hola <strong>{nombre_usuario}</strong>, gracias por unirte a nuestra comunidad.
        </p>
        <p style="font-size: 15px; color: #777; text-align: center;">
            En CandyNails estamos felices de tenerte aquí. Agenda tus citas fácilmente y descubre nuestros servicios.
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="https://prototipo-candysoft.onrender.com/" style="background-color:#d63384; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">💅 Explora CandyNails</a>
        </div>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo de registro: {e}")
        return False

def enviar_correo_cambio_password(destinatario, nombre_usuario):
    """
    Envía un correo notificando que la contraseña fue cambiada exitosamente.
    """
    asunto = "🔐 Contraseña actualizada con éxito"
    mensaje_texto = f"Hola {nombre_usuario}, tu contraseña en CandyNails ha sido cambiada correctamente."

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #f1f9f9; border-radius: 10px; border: 1px solid #d1ecf1;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/736x/ab/dd/f1/abddf13749e496af6b9bfc5f5bec55e4.jpg" alt="Cambio de contraseña" style="max-width: 120px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #0c5460; text-align: center;">🔐 Cambio de contraseña exitoso</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hola <strong>{nombre_usuario}</strong>, tu contraseña ha sido actualizada correctamente en <strong>CandyNails</strong>.
        </p>
        <p style="font-size: 15px; color: #777; text-align: center;">
            Si no fuiste tú quien realizó este cambio, por favor contacta con el soporte inmediatamente.
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="https://prototipo-candysoft.onrender.com/login" style="background-color:#d63384; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">🔐 Ir a CandyNails</a>
        </div>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo de cambio de contraseña: {e}")
        return False

def enviar_correo_confirmacion(destinatario, nombre_cliente, fecha, hora, servicios=None):
    """
    Envía un correo confirmando que la cita fue registrada exitosamente, con detalle de servicios.
    """
    asunto = "📅 Cita registrada en CandyNails"
    mensaje_texto = f"Hola {nombre_cliente}, tu cita ha sido registrada para el día {fecha} a las {hora}."

    # Construir la tabla HTML de servicios
    servicios_html = ""
    total = 0

    if servicios:
        filas = ""
        for s in servicios:
            filas += f"""
            <tr>
                <td style="padding: 8px; border: 1px solid #f8c6e0;">{s['nombre']}</td>
                <td style="padding: 8px; border: 1px solid #f8c6e0; text-align: right;">${s['subtotal']:.2f}</td>
            </tr>
            """
            total += s['subtotal']

        servicios_html = f"""
        <h3 style="color: #d63384;">🧾 Detalles de tu cita</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
            <thead>
                <tr>
                    <th style="padding: 8px; background-color: #ffe0ef; border: 1px solid #f8c6e0;">Servicio</th>
                    <th style="padding: 8px; background-color: #ffe0ef; border: 1px solid #f8c6e0; text-align: right;">Subtotal</th>
                </tr>
            </thead>
            <tbody>
                {filas}
                <tr>
                    <td style="padding: 8px; border: 1px solid #f8c6e0; font-weight: bold;">Total</td>
                    <td style="padding: 8px; border: 1px solid #f8c6e0; font-weight: bold; text-align: right;">${total:.2f}</td>
                </tr>
            </tbody>
        </table>
        """

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #fff3f8; border-radius: 10px; border: 1px solid #f8c6e0;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/736x/ab/dd/f1/abddf13749e496af6b9bfc5f5bec55e4.jpg" alt="Cita confirmada" style="max-width: 120px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #d63384; text-align: center;">📅 ¡Cita confirmada!</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hola <strong>{nombre_cliente}</strong>, tu cita ha sido registrada exitosamente para el <strong>{fecha}</strong> a las <strong>{hora}</strong>.
        </p>
        {servicios_html}
        <p style="font-size: 15px; color: #777; text-align: center;">
            Si deseas reprogramar o cancelar tu cita, comunícate con nosotros con anticipación.
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="https://prototipo-candysoft.onrender.com/" style="background-color:#d63384; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">💅 Ir a CandyNails</a>
        </div>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo de confirmación de cita: {e}")
        return False

    
def enviar_correo_bienvenida_manicurista(destinatario, nombre_empleada, contrasena, enlace_cambio_password):
    asunto = "👋 ¡Bienvenida a CandyNails!"

    mensaje_texto = f"""
    Hola {nombre_empleada},
    Has sido registrada como manicurista en CandyNails.

    Tu contraseña temporal es: {contrasena}

    Por seguridad, cambia tu contraseña usando el siguiente enlace:
    https://prototipo-candysoft.onrender.com/requerir-codigo
    """

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #fff3f8; border-radius: 10px; border: 1px solid #f8c6e0;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/736x/ab/dd/f1/abddf13749e496af6b9bfc5f5bec55e4.jpg" alt="Bienvenida" style="max-width: 120px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #d63384; text-align: center;">💅 ¡Bienvenida a CandyNails!</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hola <strong>{nombre_empleada}</strong>, has sido registrada como manicurista en nuestro sistema.
        </p>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Tu contraseña temporal es:
        </p>
        <p style="text-align: center;">
            <code style="font-size: 16px; background-color: #f3f3f3; padding: 5px 10px; border-radius: 5px;">{contrasena}</code>
        </p>
        <p style="font-size: 15px; color: #777; text-align: center;">
            Por tu seguridad, cambia tu contraseña cuanto antes usando el siguiente botón:
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="https://prototipo-candysoft.onrender.com/requerir-codigo" style="background-color:#d63384; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">🔐 Cambiar Contraseña</a>
        </div>
        <p style="font-size: 15px; color: #777; text-align: center; margin-top: 20px;">
            ¡Gracias por formar parte de nuestro equipo! 💖
        </p>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo a manicurista: {e}")
        return False
    
    
def enviar_correo_bienvenida_cliente(destinatario, nombre_cliente, contrasena, enlace_cambio_password):
    asunto = "👋 ¡Bienvenido(a) a CandyNails!"

    mensaje_texto = f"""
    Hola {nombre_cliente},
    Has sido registrada como cliente en CandyNails.

    Tu contraseña temporal es: {contrasena}

    Por seguridad, cambia tu contraseña usando el siguiente enlace:
    https://prototipo-candysoft.onrender.com/requerir-codigo
    """

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #fff3f8; border-radius: 10px; border: 1px solid #f8c6e0;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/736x/ab/dd/f1/abddf13749e496af6b9bfc5f5bec55e4.jpg" alt="Bienvenida" style="max-width: 120px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #d63384; text-align: center;">💅 ¡Bienvenido(a) a CandyNails!</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hola <strong>{nombre_cliente}</strong>, has sido registrada como cliente en nuestro sistema.
        </p>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Tu contraseña temporal es:
        </p>
        <p style="text-align: center;">
            <code style="font-size: 16px; background-color: #f3f3f3; padding: 5px 10px; border-radius: 5px;">{contrasena}</code>
        </p>
        <p style="font-size: 15px; color: #777; text-align: center;">
            Por tu seguridad, cambia tu contraseña cuanto antes usando el siguiente botón:
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="https://prototipo-candysoft.onrender.com/requerir-codigo" style="background-color:#d63384; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">🔐 Cambiar Contraseña</a>
        </div>
        <p style="font-size: 15px; color: #777; text-align: center; margin-top: 20px;">
            ¡En CandyNails estamos felices de tenerte aquí. Agenda tus citas fácilmente y descubre nuestros servicios! 💖
        </p>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo al cliente: {e}")
        return False


def enviar_correo_liquidacion_realizada(destinatario, nombre_empleada, fecha_inicial, fecha_final, comision):
    asunto = "💰 Liquidación disponible en tu perfil - CandyNails"

    mensaje_texto = f"""
    Hola {nombre_empleada},

    Se ha generado una nueva liquidación correspondiente al período del {fecha_inicial.strftime('%d/%m/%Y')} al {fecha_final.strftime('%d/%m/%Y')}.
    Comisión generada: ${comision:,.2f}

    Puedes revisar todos los detalles en tu perfil dentro del sistema.

    ¡Gracias por tu excelente trabajo!

    - Equipo CandyNails
    """

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #fff3f8; border-radius: 10px; border: 1px solid #f8c6e0;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/736x/ab/dd/f1/abddf13749e496af6b9bfc5f5bec55e4.jpg" alt="CandyNails" style="max-width: 120px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #d63384; text-align: center;">💅 ¡Nueva Liquidación Generada!</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hola <strong>{nombre_empleada}</strong>, se ha generado una liquidación correspondiente al período
            del <strong>{fecha_inicial.strftime('%d/%m/%Y')}</strong> al <strong>{fecha_final.strftime('%d/%m/%Y')}</strong>.
        </p>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Comisión generada: <strong>${comision:,.2f}</strong>
        </p>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Puedes revisar los detalles desde tu <strong>dashboard personal</strong>.
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="https://prototipo-candysoft.onrender.com/" style="background-color:#d63384; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">📋 Ir a mi Dashboard</a>
        </div>
        <p style="font-size: 15px; color: #777; text-align: center; margin-top: 20px;">
            💅 ¡Gracias por seguir haciendo un trabajo increíble! 💖
        </p>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo de liquidación: {e}")
        return False
    
def enviar_correo_bienvenida_empleado(destinatario, nombre_empleado, contrasena, enlace_cambio_password, rol_usuario):
    asunto = "👋 ¡Bienvenido(a) a CandyNails!"

    rol_legible = rol_usuario.capitalize()

    mensaje_texto = f"""
    Hola {nombre_empleado},
    Has sido registrado(a) como {rol_legible} en CandyNails.

    Tu contraseña temporal es: {contrasena}

    Por seguridad, cambia tu contraseña usando el siguiente enlace:
    https://prototipo-candysoft.onrender.com/requerir-codigo
    """

    mensaje_html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background-color: #fff3f8; border-radius: 10px; border: 1px solid #f8c6e0;">
        <div style="text-align: center;">
            <img src="https://i.pinimg.com/736x/ab/dd/f1/abddf13749e496af6b9bfc5f5bec55e4.jpg" alt="Bienvenida" style="max-width: 120px; margin-bottom: 20px;" />
        </div>
        <h2 style="color: #d63384; text-align: center;">💅 ¡Bienvenido(a) a CandyNails!</h2>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Hola <strong>{nombre_empleado}</strong>, has sido registrado(a) como <strong>{rol_legible}</strong> en nuestro sistema.
        </p>
        <p style="font-size: 16px; color: #555; text-align: center;">
            Tu contraseña temporal es:
        </p>
        <p style="text-align: center;">
            <code style="font-size: 16px; background-color: #f3f3f3; padding: 5px 10px; border-radius: 5px;">{contrasena}</code>
        </p>
        <p style="font-size: 15px; color: #777; text-align: center;">
            Por tu seguridad, cambia tu contraseña cuanto antes usando el siguiente botón:
        </p>
        <div style="text-align: center; margin-top: 20px;">
            <a href="https://prototipo-candysoft.onrender.com/requerir-codigo" style="background-color:#d63384; color: white; padding: 12px 20px; text-decoration: none; border-radius: 5px;">🔐 Cambiar Contraseña</a>
        </div>
        <p style="font-size: 15px; color: #777; text-align: center; margin-top: 20px;">
            ¡Gracias por formar parte de nuestro equipo! 💖
        </p>
    </div>
    """

    try:
        send_mail(
            subject=asunto,
            message=mensaje_texto,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[destinatario],
            html_message=mensaje_html,
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Error al enviar correo a {rol_legible}: {e}")
        return False
