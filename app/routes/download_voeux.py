"""
download_voeux.py
Ce fichier gère les fonctionnalités liées au téléchargement des vœux des utilisateurs dans différents formats 
(CSV, Excel, PDF). Il est utilisé dans le cadre d'une application Flask pour permettre aux utilisateurs 
de récupérer leurs vœux ou ceux des élèves d'une classe, selon leurs droits d'accès.
Fonctionnalités principales :
- Téléchargement des vœux d'un utilisateur connecté dans les formats CSV, Excel ou PDF.
- Téléchargement des vœux de plusieurs élèves d'une classe pour les utilisateurs ayant des droits 
    spécifiques (professeurs ou administrateurs).
- Génération de fichiers PDF avec mise en page personnalisée, incluant des tableaux et des numéros de page.
- Gestion des droits d'accès pour sécuriser les données et restreindre les fonctionnalités selon le rôle 
    de l'utilisateur.
- Exportation des données dans des formats adaptés pour une utilisation ultérieure (analyse, impression, etc.).
Ce fichier utilise des bibliothèques comme Flask, pandas, xlsxwriter et ReportLab pour gérer les 
différents formats de fichiers et les fonctionnalités associées.
"""

from flask import Flask, request, render_template, redirect, url_for, flash, session, make_response, jsonify, abort, send_file
from ext_config import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlmodel import Session, select
import json
import uuid
from flask_socketio import SocketIO, emit, join_room, leave_room
import pandas as pd
import io
import xlsxwriter
from reportlab.lib.pagesizes import landscape
from reportlab.pdfgen import canvas
import logging
from ds import send_discord_message

from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageBreak
from reportlab.lib.pagesizes import landscape, letter, A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle

def download_voeux():
    session_cookie = request.cookies.get('session_cookie')
    app.logger.info("Client IP: %s", get_client_ip())
    app.logger.info("Session cookie: %s", session_cookie)

    with Session(engine) as session:
        user = get_user_by_cookie(session, session_cookie)
        if user.professeur or user.admin:
            flash("Vous n'avez pas les droits pour accéder à cette page.", "error")
            return redirect(url_for('dashboard'))

    format = request.args.get('format', 'csv')
    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if user and user.voeux_etablissements:
                voeux = json.loads(user.voeux_etablissements)
                df = pd.DataFrame(voeux)
                if 'enable' in df.columns:
                    df = df[df['enable'] == True]
                    df.drop(columns=['enable'], inplace=True)
                
                # Renommer les colonnes
                df.rename(columns={
                    "row_number": "#",
                    "school": "Nom de l'établissement",
                    "city": "Ville",
                    "degree": "Type de Voie",
                    "specialization": "Spécialité"
                }, inplace=True)
                
                output = io.BytesIO()
                if format == 'xls':
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, index=False, sheet_name='Voeux')
                    output.seek(0)
                    app.logger.info("Voeux téléchargés pour l'utilisateur: %s", user.identifiant_unique)
                    send_discord_message("eleve_telecharge_pdf_xlsx", user.identifiant_unique, get_url_from_request(request))
                    return send_file(
                        output,
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                        as_attachment=True,
                        download_name='voeux.xlsx'
                    )
                elif format == 'pdf':
                    # Définir une taille de page personnalisée (par exemple, 11x17 pouces en paysage)
                    output = io.BytesIO()
                    doc = SimpleDocTemplate(output, pagesize=landscape(A4))
                    styles = getSampleStyleSheet()
                    elements = []

                    # Ajouter un titre
                    title = Paragraph(f"Voeux de l'élève: {user.identifiant_unique} - {user.niveau_classe}", styles['Title'])
                    elements.append(title)

                    # Préparer les données pour le tableau
                    data = [df.columns.tolist()]  # Ajouter les en-têtes de colonnes

                    # Style pour le texte dans les cellules
                    cell_style = ParagraphStyle(name="CellStyle", fontSize=10, leading=12)

                    # Ajouter les lignes de données avec gestion des sauts de ligne
                    for _, row in df.iterrows():
                        formatted_row = [Paragraph(str(cell), cell_style) for cell in row]
                        data.append(formatted_row)

                    # Ajuster les largeurs des colonnes
                    col_widths = [25, 150, 150, 150, 325]  # Largeurs personnalisées pour chaque colonne
                    table = Table(data, colWidths=col_widths, repeatRows=1)

                    # Appliquer le style au tableau
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ]))
                    elements.append(table)

                    # Générer le PDF
                    def add_page_number(canvas, doc):
                        # Obtenir le numéro de la page actuelle
                        page_num = canvas.getPageNumber()
                        # Ajouter le texte 'Page X' en bas au centre
                        text = f"Page {page_num}"
                        canvas.drawCentredString(415, 15, text)  # Positionner le texte au centre en bas de la page

                    # Générer le PDF avec les numéros de page
                    doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
                    output.seek(0)
                    send_discord_message("eleve_telecharge_pdf_xlsx", user.identifiant_unique, get_url_from_request(request))
                    return send_file(
                        output,
                        mimetype='application/pdf',
                        as_attachment=True,
                        download_name='voeux.pdf'
                    )
                else:  # Default to CSV
                    output = io.StringIO()
                    df.to_csv(output, index=False)
                    output.seek(0)
                    app.logger.info("Voeux téléchargés pour l'utilisateur: %s", user.identifiant_unique)
                    return send_file(
                        io.BytesIO(output.getvalue().encode()),
                        mimetype='text/csv',
                        as_attachment=True,
                        download_name='voeux.csv'
                    )
            else:
                return jsonify({'error': 'User not found or no voeux available'}), 404
    else:
        return jsonify({'error': 'No session cookie'}), 400




def download_voeux_users_classe():
    session_cookie = request.cookies.get('session_cookie')
    format = request.args.get('format', 'csv')

    if session_cookie:
        with Session(engine) as session:
            user = get_user_by_cookie(session, session_cookie)
            if user:
                if not user.professeur:
                    flash("Vous n'avez pas les droits pour accéder à cette page.", "error")
                    return jsonify({'error': 'User is not a professor'}), 403

    data = request.get_json()
    selected_ids = data.get('selected_ids', [])

    if not selected_ids:
        return jsonify({'error': 'No student IDs provided'}), 400

    with Session(engine) as session:
        students = session.exec(select(Users).where(Users.identifiant_unique.in_(selected_ids))).all()

    if format == 'pdf':
        output = io.BytesIO()
        doc = SimpleDocTemplate(output, pagesize=landscape(A4))
        styles = getSampleStyleSheet()
        elements = []

        for student in students:
            # Ajouter un titre pour chaque élève
            title = Paragraph(f"Voeux de l'élève: {student.identifiant_unique} - {student.niveau_classe}", styles['Title'])
            elements.append(title)

            # Préparer les données des vœux de l'élève
                        # Préparer les données des vœux de l'élève
            voeux = json.loads(student.voeux_etablissements)
            voeux = [v for v in voeux if v.get('enable') == True]  # Filtrer les vœux où enable == True
            
            if voeux:
                # Ajouter les en-têtes de colonnes
                data = [['#', 'Nom de l\'établissement', 'Ville', 'Diplôme', 'Spécialisation']]
            
                # Style pour le texte dans les cellules
                cell_style = ParagraphStyle(name="CellStyle", fontSize=10, leading=12)
            
                # Ajouter les lignes de données avec gestion des sauts de ligne
                for v in voeux:
                    formatted_row = [
                        Paragraph(str(v['row_number']), cell_style),  # Colonne #
                        Paragraph(str(v['school']), cell_style),
                        Paragraph(str(v['city']), cell_style),
                        Paragraph(str(v['degree']), cell_style),
                        Paragraph(str(v['specialization']), cell_style)
                    ]
                    data.append(formatted_row)
            
                # Ajuster les largeurs des colonnes
                col_widths = [25, 150, 150, 150, 325]  # Largeurs personnalisées pour chaque colonne
                table = Table(data, colWidths=col_widths, repeatRows=1)
            
                # Appliquer le style au tableau
                                # Appliquer le style au tableau
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Fond gris pour les en-têtes
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Texte blanc pour les en-têtes
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Centrer tout le texte dans le tableau
                    ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Centrer spécifiquement la colonne #
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Police en gras pour les en-têtes
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding en bas pour les en-têtes
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grille noire pour toutes les cellules
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),  # Aligner verticalement au milieu
                ]))
                elements.append(table)
            else:
                # Ajouter un message centré si aucun vœu n'est disponible
                no_voeux_message = Paragraph(
                    "Cet élève n'a ajouté aucun vœux dans son tableau de pré-classement",
                    ParagraphStyle(name="NoVoeuxStyle", fontSize=12, alignment=1)  # Alignment 1 = centré
                )
                elements.append(no_voeux_message)

            # Ajouter un saut de page après chaque élève
            elements.append(PageBreak())

        # Générer le PDF
        def add_page_number(canvas, doc):
            # Obtenir le numéro de la page actuelle
            page_num = canvas.getPageNumber()
            # Ajouter le texte 'Page X' en bas au centre
            text = f"Page {page_num}"
            canvas.drawCentredString(415, 15, text)  # Positionner le texte au centre en bas de la page

        # Générer le PDF avec les numéros de page
        doc.build(elements, onFirstPage=add_page_number, onLaterPages=add_page_number)
        output.seek(0)
        send_discord_message("prof_telecharge_pdf_xlsx", user.identifiant_unique, get_url_from_request(request))
        return send_file(
            output,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='voeux_eleves.pdf'
        )
    else:
        data = []
        for student in students:
            voeux = json.loads(student.voeux_etablissements)
            voeux = [v for v in voeux if v.get('enable') == True]  # Filtrer les vœux où enable == True
            for v in voeux:
                data.append([
                    student.identifiant_unique,
                    v['row_number'],
                    v['school'],
                    v['city'],
                    v['degree'],
                    v['specialization']
                ])

        # Ajouter les en-têtes de colonnes
        headers = ['ID', '#', 'Nom de l\'établissement', 'Ville', 'Type de Voie', 'Spécialité']
        data.insert(0, headers)

        # Créer un DataFrame pour l'exportation
        df = pd.DataFrame(data[1:], columns=headers)

        output = io.BytesIO()

        if format == 'xlsx':
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Voeux')
            output.seek(0)
            send_discord_message("prof_telecharge_pdf_xlsx", user.identifiant_unique, get_url_from_request(request), get_client_ip())
            return send_file(
            output,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name='voeux.xlsx'
            )


        else:  # Default to CSV
            output = io.StringIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(
                io.BytesIO(output.getvalue().encode()),
                mimetype='text/csv',
                as_attachment=True,
                download_name='voeux_elevesigiy.csv'
            )