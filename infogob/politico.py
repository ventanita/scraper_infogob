# -*- coding: utf-8 -*-
# Copyright 2015 by Pedro Palacios. All rights reserved.
# This code is part of the Ventanita distribution and governed by its
# license. Please see the LICENSE file that should have been included
# as part of this package.
from bs4 import BeautifulSoup
import requests as req
import re


def data_busqueda(dni):
    """ Form_data de la peticion, recibe el dni del candidato como str
    o como int"""
    if type(dni) == int:
        dni = str(dni).zfill(8)
    assert len(dni) == 8, "El dni no tiene 8 cifras"
    return {
        "__LASTFOCUS": "",
        "__EVENTTARGET": "",
        "__EVENTARGUMENT": "",
        "__VIEWSTATE": "".join(["jbOIeiP8rXhqSrKOfJ8kCoQqnwz1ZypA3Y",
                               "fq+mzWEt1rlNo/eI7YJiBRzm1ON4lVmixk",
                               "o9gD6TmCtFO2UjMOBLbw8JqlT+vqPCokS1",
                               "yK0FNZuE6dfGVAaQYBny457nWEwWj0cewA",
                               "1PfbsniLM3BV01T8tUOmggI/Awby1XmpWE",
                               "ziTH4RgGD6GcZnBj9xKn1IlrOuSNgQn4U6",
                               "Bkdu/3DvxG/aP/ZWaQ8tGZ//+ymwoCp6ZH",
                               "0SB96crhKvHbKpMQmPv2+a2RfRXs0GXiBq",
                               "ARELDhMlpyaghuR0ur5+cMTFn9lRK65dm4",
                               "pB7pCeoVehZehVIwevVMoXRZb3Ce4os7zT",
                               "1b0ysAHKUhLoPNvPHoqSEPWIEJz9PBQqtk",
                               "Dkc3GNTDhmdNsqc2rfyu39XF6VkMZJKg=="]),
        "__VIEWSTATEENCRYPTED": "",
        "__EVENTVALIDATION": "".join(["lExKGGy68x6C7WZJvzBZg8z7uIbk",
                                     "IgFcyOrCRPfOtTUgyI08/fmHw1/s",
                                     "aY9vuaxD"]),
        "ctl00$ContentPlaceHolder1$txt_nombres": "",
        "ctl00$ContentPlaceHolder1$txt_paterno": "",
        "ctl00$ContentPlaceHolder1$txt_materno": "",
        "ctl00$ContentPlaceHolder1$txt_dni": dni,
        "ctl00$ContentPlaceHolder1$ImgBtnAceptar.x": 0,
        "ctl00$ContentPlaceHolder1$ImgBtnAceptar.y": 0,
    }


def get_id_pol(dni):
    """Realiza la peticion y devuelve el id_politico"""
    url_base = "http://www.infogob.com.pe/Politico/politico.aspx"
    form_data = data_busqueda(dni)
    res = req.post(url_base, data=form_data)
    soup = BeautifulSoup(res.text)
    tabla = soup.find("table", class_="mygrid")
    assert tabla, "Mala peticion"
    rows = tabla.find_all("tr")
    if len(rows) == 1:
        return None
    assert len(rows) == 2, "La busqueda devolvio varios resultados"
    row_cand = rows[1]
    link = row_cand.find("a").attrs["href"]
    match = re.search("IdPolitico=(?P<id>\d+)", link)
    assert len(match.groups()) == 1, ("Id no encontrado en link {link}"
                                     .format(link=link))
    return match.group("id")


def get_soup_ficha(id_politico, tab=0):
    """Consigue la ficha del candidato, por defecto selecciona la primera
    pestaña"""
    url_ficha = ("".join(["http://www.infogob.com.pe/Politico/",
                         "ficha.aspx?IdPolitico={id_pol}&IdTab={tab}"])
                 .format(id_pol=id_politico, tab=tab))
    res = req.get(url_ficha)
    return BeautifulSoup(res.text)


def get_dic_links(soup_ficha):
    """Devuelve un diccionario con los links a la hoja de vida, plan de gobierno
    y declaracion jurada de bienes y rentas del candidato"""
    tablas_enlaces = soup_ficha.find(id="generales-enlace")
    return {"hoja_vida": tablas_enlaces.find(id="ctl00_ContentPlaceHolder1_cabecera1_hlk_HojaVida").attrs.get("href"),
            "plan_gobierno": tablas_enlaces.find(id="ctl00_ContentPlaceHolder1_cabecera1_hlk_PlanGobierno").attrs.get("href"),
            "declaracion_bienes": tablas_enlaces.find(id="ctl00_ContentPlaceHolder1_cabecera1_hlk_DJ").attrs.get("href"),
    }


def get_dic_datos(soup_ficha):
    fields = soup_ficha.find(id="generales-dato")
    return {
        "dni": unicode(fields.find(id="ctl00_ContentPlaceHolder1_cabecera1_LblDni").string),
        "nombre": unicode(fields.find(id="ctl00_ContentPlaceHolder1_cabecera1_LblNombres").string),
        "nacimiento": unicode(fields.find(id="ctl00_ContentPlaceHolder1_cabecera1_LblFecNacimiento").string),
        "residencia": {
            "region": unicode(fields.find(id="ctl00_ContentPlaceHolder1_cabecera1_LblRegion").string),
            "provincia": unicode(fields.find(id="ctl00_ContentPlaceHolder1_cabecera1_LblProvincia").string),
            "distrito": unicode(fields.find(id="ctl00_ContentPlaceHolder1_cabecera1_LblDistrito").string),
        }
    }

if __name__ == "__main__":
    assert get_id_pol(8051943) == '2398026', "Error en 'get_id_pol' (el id del politico cambio?)"
