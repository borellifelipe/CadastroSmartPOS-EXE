from tkinter import Tk, Label, BooleanVar, StringVar, Checkbutton, OptionMenu, Button, messagebox
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

formas_pagamento = [
    "Crédito Mastercard", "Débito Mastercard", "Crédito Elo", "Débito Elo",
    "Crédito Visa", "Débito Visa", "Crédito Amex", "Crédito Hipercard", "Pix"
]
parceiros_disponiveis = ["Stone", "PagSeguro", "Rede", "Ifood Pago"]
bandeiras_disponiveis = [
    "Visa", "Mastercard", "American Express", "Sorocred", "Diners Club", "Elo", "Hipercard", "Cabal",
    "Aura", "Banes Card", "Alelo", "Sicredi", "Cresol", "CalCard", "Discover", "GoodCard", "GreenCard",
    "JCB", "Mais", "MaxVan", "Policard", "RedeCompras", "Sodexo", "ValeCard", "Verocheque", "VR", "Ticket", "Outros"
]

def conectar_chrome():
    chrome_options = Options()
    chrome_options.debugger_address = "127.0.0.1:9222"
    return webdriver.Chrome(options=chrome_options)

def localizar_botao_nova_fp(driver, wait):
    seletores = [
        (By.XPATH, "//button[@title='Incluir']"),
        (By.XPATH, "//button[.//i[contains(@class, 'zmdi-plus')]]"),
        (By.CSS_SELECTOR, "button.bgm-red.btn-icon"),
        (By.XPATH, "//button[contains(@class,'bgm-red')]"),
    ]
    for tipo, seletor in seletores:
        try:
            driver.execute_script("window.scrollTo(0, 0);")
            botao = wait.until(EC.element_to_be_clickable((tipo, seletor)))
            return botao
        except Exception:
            continue
    return None

def clicar_aba_pagamento_app_garcom(driver, wait):
    aba_xpath = "//a[contains(translate(normalize-space(.), 'ABCDEFGHIJKLMNOPQRSTUVWXYZÁÂÃÉÊÍÓÔÕÚÇ', 'abcdefghijklmnopqrstuvwxyzáâãéêíóôõúç'), 'pagamento app garçom')]"
    aba = wait.until(EC.presence_of_element_located((By.XPATH, aba_xpath)))
    driver.execute_script("""
        let el = arguments[0];
        let li = el.parentElement;
        if (li) li.classList.remove('disabled');
        el.classList.remove('disabled');
        el.style.pointerEvents = 'auto';
        el.style.display = 'block';
        el.removeAttribute('disabled');
        el.tabIndex = 0;
    """, aba)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", aba)
    driver.execute_script("arguments[0].click();", aba)
    time.sleep(0.3)

def marcar_checkbox_garcom(driver, wait):
    xpath = "//input[@type='checkbox' and contains(@ng-model,'vm.record.enabled_pos_integration')]"
    checkbox = wait.until(EC.presence_of_element_located((By.XPATH, xpath)))
    if not checkbox.is_selected():
        driver.execute_script("arguments[0].click();", checkbox)
    time.sleep(0.05)

def selecionar_dropdown_por_label(driver, wait, label_text, option_texts, obrigatorio=False, tempo=0.15, custom_wait=None):
    if isinstance(option_texts, str):
        option_texts = [option_texts]
    try:
        driver.find_element(By.TAG_NAME, 'body').click()
        time.sleep(0.05)
        local_wait = WebDriverWait(driver, custom_wait) if custom_wait else wait
        dropdown = local_wait.until(EC.element_to_be_clickable((
            By.XPATH, f"//label[contains(.,'{label_text}')]/following-sibling::*//a[contains(@class,'chosen-single')]"
        )))
        dropdown.click()
        time.sleep(tempo)
        for option_text in option_texts:
            try:
                option_xpath = f"//ul[contains(@class,'chosen-results')]//li[normalize-space()='{option_text}']"
                item = local_wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
                driver.execute_script("arguments[0].scrollIntoView();", item)
                item.click()
                time.sleep(tempo)
                return
            except Exception:
                try:
                    option_xpath = f"//ul[contains(@class,'chosen-results')]//li[contains(.,'{option_text}')]"
                    item = local_wait.until(EC.element_to_be_clickable((By.XPATH, option_xpath)))
                    driver.execute_script("arguments[0].scrollIntoView();", item)
                    item.click()
                    time.sleep(tempo)
                    return
                except Exception:
                    continue
        raise Exception(f"Opção(s) '{option_texts}' não encontrada(s) para '{label_text}'")
    except Exception as e:
        if obrigatorio:
            raise Exception(f"Erro ao selecionar dropdown '{label_text}' para opção(s) '{option_texts}': {str(e)}")
        else:
            print(f"Dropdown '{label_text}' não localizado ou não obrigatório: {option_texts} ({e})")

def parse_metodo_forma_bandeira(descricao, parceiro):
    desc = descricao.lower()
    if "crédito" in desc:
        metodo = "Cartão de Crédito"
        forma = "Crédito"
    elif "débito" in desc:
        metodo = "Cartão de Débito"
        forma = "Débito"
    elif "pix" in desc:
        metodos_pix = ["Pagamento Instantâneo (PIX)", "Pix", "PIX", "Pagamento Instantâneo"]
        formas_pix = ["Carteira Digital (PIX)", "Pix", "PIX", "Carteira Digital", "Pagamento Instantâneo (PIX)"]
        return metodos_pix, formas_pix, None
    elif "voucher" in desc:
        metodo = "Voucher"
        forma = "Voucher"
    else:
        metodo = None
        forma = None
    bandeira = None
    if "amex" in desc or "american express" in desc:
        bandeira = "American Express"
    else:
        for b in bandeiras_disponiveis:
            if b.lower() in desc:
                bandeira = b
                break
    return metodo, forma, bandeira

def clicar_salvar(driver, wait, custom_wait=None):
    try:
        # Turbo: clica por JS assim que existir no DOM!
        salvar_btn = driver.find_element(By.XPATH, "//button[contains(., 'SALVAR') and not(contains(.,'CÓPIA'))]")
        driver.execute_script("arguments[0].scrollIntoView();", salvar_btn)
        driver.execute_script("arguments[0].click();", salvar_btn)
        time.sleep(0.05)
        return True
    except Exception as e:
        print(f"SALVAR padrão não funcionou, tentando XPATH absoluto fornecido.")
        try:
            salvar_btn = driver.find_element(By.XPATH, "/html/body/div[7]/div/div/form/div[2]/button[3]")
            driver.execute_script("arguments[0].scrollIntoView();", salvar_btn)
            driver.execute_script("arguments[0].click();", salvar_btn)
            time.sleep(0.05)
            return True
        except Exception as ee:
            raise Exception(f"Erro ao clicar no botão SALVAR: {str(ee)}")

def iniciar_automacao(selecionados, parceiro):
    driver = conectar_chrome()
    driver.get("https://conta.saipos.com/#/app/store/payment-type")
    time.sleep(3.0)
    wait = WebDriverWait(driver, 14)

    parceiros_rapidos = ["PagSeguro", "Rede", "Ifood Pago"]

    for nome in selecionados:
        try:
            botao_nova_fp = localizar_botao_nova_fp(driver, wait)
            if not botao_nova_fp:
                driver.save_screenshot(f"erro_botao_fp_{nome}.png")
                messagebox.showerror("Erro", f"Botão '+ Forma de pagamento' não localizado.\nScreenshot: erro_botao_fp_{nome}.png")
                driver.quit()
                return
            botao_nova_fp.click()
            time.sleep(0.55)

            desc_input = wait.until(
                EC.visibility_of_element_located((By.XPATH, "//label[contains(.,'Descrição')]/following-sibling::input[@type='text' and not(@disabled)]"))
            )
            desc_input.clear()
            desc_input.send_keys(nome)
            time.sleep(0.10)

            metodo, forma_pagamento, bandeira = parse_metodo_forma_bandeira(nome, parceiro)

            tempo_metodo = 0.07
            if "pix" in nome.lower() and parceiro in parceiros_rapidos:
                tempo_forma = 0.01
                custom_wait_forma = 0.3   # Ultra rápido!
                custom_wait_salvar = 0.3   # Ultra rápido para salvar!
            else:
                tempo_forma = 0.07
                custom_wait_forma = None
                custom_wait_salvar = None

            if metodo:
                selecionar_dropdown_por_label(driver, wait, "Método de pagamento", metodo, obrigatorio=True, tempo=tempo_metodo)
            if bandeira and not ("pix" in nome.lower()):
                selecionar_dropdown_por_label(driver, wait, "Bandeira do cartão", bandeira, obrigatorio=True, tempo=0.10)

            clicar_aba_pagamento_app_garcom(driver, wait)
            marcar_checkbox_garcom(driver, wait)
            selecionar_dropdown_por_label(driver, wait, "Parceiro", parceiro, obrigatorio=True, tempo=0.11)

            if "pix" in nome.lower():
                selecionar_dropdown_por_label(driver, wait, "Forma de pagamento", forma_pagamento, obrigatorio=True, tempo=tempo_forma, custom_wait=custom_wait_forma)
            elif forma_pagamento:
                selecionar_dropdown_por_label(driver, wait, "Forma de pagamento", forma_pagamento, obrigatorio=True, tempo=0.11)
            else:
                raise Exception(f"Não foi possível determinar a 'Forma de pagamento' para a descrição: {nome}")

            clicar_salvar(driver, wait, custom_wait=custom_wait_salvar)
            time.sleep(0.05)

        except Exception as e:
            driver.save_screenshot(f"erro_cadastro_{nome}.png")
            messagebox.showerror("Erro", f"Erro ao cadastrar {nome}:\nMensagem:\n{str(e)}.\nScreenshot: erro_cadastro_{nome}.png")
            driver.quit()
            return

    messagebox.showinfo("Concluído", "Formas de pagamento cadastradas com sucesso!")
    driver.quit()

def executar_gui():
    root = Tk()
    root.title("Cadastro de Formas de Pagamento")
    Label(root, text="Selecione as formas de pagamento:").pack()
    variaveis = {}
    for forma in formas_pagamento:
        var = BooleanVar()
        Checkbutton(root, text=forma, variable=var).pack(anchor="w")
        variaveis[forma] = var

    Label(root, text="Selecione o parceiro:").pack()
    parceiro_var = StringVar(root)
    parceiro_var.set(parceiros_disponiveis[0])
    OptionMenu(root, parceiro_var, *parceiros_disponiveis).pack()

    def ao_clicar():
        selecionadas = [nome for nome, var in variaveis.items() if var.get()]
        if not selecionadas:
            messagebox.showwarning("Aviso", "Selecione ao menos uma forma de pagamento.")
            return
        iniciar_automacao(selecionadas, parceiro_var.get())

    Button(root, text="Cadastrar", command=ao_clicar).pack(pady=10)
    root.mainloop()

if __name__ == "__main__":
    executar_gui()

#Mostrando que a automaçao funciona em segundo plano