from a_apis.models.email_verification import EmailVerification

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone


class EmailService:
    @staticmethod
    def send_verification_email(email: str) -> dict:
        try:
            # 기존 미인증 코드 삭제
            EmailVerification.objects.filter(email=email, is_verified=False).delete()

            # 새로운 인증 코드 생성
            verification = EmailVerification.objects.create(email=email)

            # 이메일 내용 구성
            verification_link = f"{settings.SERVER_BASE_URL}/api/users/verify-email?code={verification.verification_code}"
            subject = "이메일 인증을 완료해주세요"
            message = f"""
                이메일 인증을 완료하려면 아래 링크를 클릭하세요:
                {verification_link}
                
                이 링크는 24시간 동안 유효합니다.
            """
            html_message = f"""
                <html>
                    <body>
                        <h2>이메일 인증</h2>
                        <p>아래 링크를 클릭하여 이메일 인증을 완료해주세요:</p>
                        <a href="{verification_link}">이메일 인증하기</a>
                        <p>이 링크는 24시간 동안 유효합니다.</p>
                    </body>
                </html>
            """

            # 이메일 전송
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )

            return {
                "success": True,
                "message": "인증 이메일이 발송되었습니다. 이메일을 확인해주세요.",
            }

        except Exception as e:
            return {
                "success": False,
                "message": f"이메일 전송 중 오류가 발생했습니다: {str(e)}",
            }

    @staticmethod
    def verify_email(verification_code: str) -> dict:
        try:
            verification = EmailVerification.objects.get(
                verification_code=verification_code, is_verified=False
            )

            if verification.is_expired:
                return {
                    "success": False,
                    "message": "인증 코드가 만료되었습니다. 다시 시도해주세요.",
                }

            verification.is_verified = True
            verification.save()

            return {"success": True, "message": "이메일 인증이 완료되었습니다."}

        except EmailVerification.DoesNotExist:
            return {"success": False, "message": "유효하지 않은 인증 코드입니다."}
        except Exception as e:
            return {
                "success": False,
                "message": f"처리 중 오류가 발생했습니다: {str(e)}",
            }
