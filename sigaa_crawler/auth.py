from playwright.sync_api import Page

LOGIN_URL = "https://sigaa.ufcg.edu.br/sigaa/verTelaLogin.do"


def login(page: Page, usuario: str, senha: str) -> None:
    page.goto(LOGIN_URL)
    page.fill('input[name="user.login"]', usuario)
    page.fill('input[name="user.senha"]', senha)
    page.click('input[type="submit"][value="Entrar"]')
    page.wait_for_load_state("networkidle")

    if page.locator('input[name="user.senha"]').count() > 0:
        raise RuntimeError(
            "Login falhou: a tela de login ainda está presente após o envio. "
            "Verifique SIGAA_USER e SIGAA_SENHA no .env."
        )
