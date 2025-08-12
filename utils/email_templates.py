def render_email_template(message=""):
    """
    Renders the email template with the provided body and subject.
    
    Args:
        body (str): The body of the email.
        subject (str): The subject of the email.
    
    Returns:
        str: The rendered HTML email template.
    """
    html = f"""\
        <html lang="en">
        <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <style>
            body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333333;
            background-color: #ffffff;
            }}
            .container {{
            max-width: 600px;
            margin: auto;
            padding: 20px;
            }}
            .logo {{
            text-align: center;
            margin-bottom: 20px;
            }}
            .logo img {{
            width: 150px;
            }}
            /* .content {{
            background-color: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            }} */
            .content h2 {{
            color: #111111;
            }}
            .content p {{
            line-height: 1.6;
            }}
            .highlight {{
            font-weight: bold;
            }}
            a {{
            color: #007bff;
            text-decoration: none;
            }}
            .footer {{
            text-align: center;
            font-size: 14px;
            margin-top: 30px;
            color: #666;
            }}
            .social-icons {{
            margin-top: 10px;
            }}
            .social-icons img {{
            width: 24px;
            margin: 0 5px;
            vertical-align: middle;
            }}
            @media (max-width: 600px) {{
            .container {{
                padding: 15px;
            }}
            .content {{
                padding: 15px;
            }}
            }}
        </style>
        </head>
        <body>
        <div class="container">
            <div class="logo">
            <img src="https://pycontg.pytogo.org/static/images/pycontogo.png" alt="PyCon TOGO 2025 Logo">
            </div>
            <div class="content">

           {message}

            <p><strong>Best regards,</strong></p>
        </div>

            <div class="footer">
            <!-- <img class="logo" src="static/images/pycontogo.png" alt="PyCon TOGO 2025 Logo"> -->
            <p><strong>Python Togo Community</strong><br>
            <a href="https://wwww.pytogo.org/">Python TOGO</a><br>
            Bd de la KARA, +22898273805  / +22898776682 / +22892555987 , LOME</p>

            <div class="social-icons">
                <a href="#"><img src="https://cdn-icons-png.flaticon.com/512/145/145807.png" alt="LinkedIn"></a>
                <a href="https://pytogo.org/discord"><img src="https://cdn-icons-png.flaticon.com/512/5968/5968756.png" alt="Discord"></a>
                <a href="https://github.com/pytogo-org"><img src="https://cdn-icons-png.flaticon.com/512/25/25231.png" alt="GitHub"></a>
                <a href="https://x.com/pytogo_org"><img src="https://cdn-icons-png.flaticon.com/512/733/733635.png" alt="X/Twitter"></a>
                <a href="https://www.youtube.com/@PythonTogo"><img src="https://cdn-icons-png.flaticon.com/512/1384/1384060.png" alt="YouTube"></a>
                <a href="#"><img src="https://cdn-icons-png.flaticon.com/512/1384/1384063.png" alt="Instagram"></a>
            </div>
            </div>
        </div>
        </body>
        </html>
    """
    return html