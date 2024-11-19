import random, os, subprocess, shutil, glob, yaml

def generate_problems(p_info, rows, cols, largest):
    new_problems = []
    smallest = 1
    a = 0
    b = 0
    if p_info[0]=='addition':

        if p_info[1]=='max':
            ub = p_info[2]
            for _ in range(rows * cols):
                a1 = a
                b1 = b
                while a1 == a and b1 == b:  # Ensure the same problem does not appear twice in a row
                    if ub> 0:
                        a = random.randint(smallest, min(largest, ub))
                        b = random.randint(smallest, min(largest, ub - a))  # Ensures sum is <= max_value
                    else:
                        a = random.randint(smallest, largest)
                        b = random.randint(smallest, largest)  # Ensures sum is <= max_value
                new_problems.append((a, b))

    elif p_info[0]=='subtraction':
        for _ in range(rows * cols):
            a1 = a
            b1 = b
            while a1 == a and b1 == b: #Ensure the same problem does not appear twice in a row
                a = random.randint(2, largest)
                if p_info[1] == 'smallest term':
                    b = random.randint(1, min(p_info[2],a - 1))  # Ensures the term being subtracted is at most p_info[2].
                elif p_info[1] == 'difference':
                    b = random.randint(max(1, a - p_info[2]), a - 1)  # Ensures the difference is at most p_info[2]
            new_problems.append((a, b))

    return new_problems


def create_latex(rows, cols, int_pairs, p_type, description):
    latex_content = r"""\documentclass{article}
\usepackage[fontsize=20pt]{fontsize}
\usepackage[letterpaper, margin=1in]{geometry}
\usepackage{xlop}
\usepackage{graphicx}

\newcommand\Block[1]{%
\setlength\fboxsep{0pt}\setlength\fboxrule{0.1pt}% delete
\fbox{% delete
\begin{minipage}[c][.2\textheight][t]{0.2\textwidth}
#1
\end{minipage}%
  }% delete
}

\newcommand\gobble[1]{}% Print <nothing> regardless of input

\begin{document}

\pagenumbering{gobble}

\noindent
\begin{minipage}[t]{1.3cm}
\includegraphics[scale=0.1]{/Users/vlamis/GitHub/DailyMath/WorksheetGenerator/TeX/cat-abacus}
\end{minipage}
\raisebox{1ex}{
\begin{minipage}[c]{4cm}
	DailyMath.{\tiny{education}}
\end{minipage}}
\hfill {\scriptsize \today }

\smallskip
\hrule

\bigskip
\noindent
{\scriptsize """ + description + r"""}

\bigskip
\noindent
"""


    for i in range(rows):

        for j in range(cols):
            x = int_pairs[5*i+j][0]
            y = int_pairs[5*i+j][1]
            latex_content = (latex_content +
                             ('\\Block{ \n'
                              '\\[ \n'
                              '	\\begin{array}{l r}\n'
                              f'			& {x} \\\\\n'))
            if p_type == 'addition':
                latex_content = latex_content + f'		+	& {y} \\\\\n'
            elif p_type == 'subtraction':
                latex_content = latex_content + f'		-	& {y} \\\\\n'

            latex_content = (latex_content +
                             ('	    \hline\n'
                              '	\end{array}\n'
                              '\\]\n'
                              '}%\n'))

        if i < rows-1:
            latex_content = latex_content + r'\par\nointerlineskip\noindent'+'\n'

    latex_content = latex_content + r'\end{document}'
    return latex_content


def save_latex_file(content, filename="TeX/worksheet.tex"):
    with open(filename, "w") as lfile:
        lfile.write(content)


def generate_pdf(tex_file_path):
    compile_dir = os.path.dirname(tex_file_path)
    tex_file_name = os.path.basename(tex_file_path)
    subprocess.run(["pdflatex", "-interaction=batchmode", tex_file_name], cwd=compile_dir, check=True)
    print(f"PDF generated at {compile_dir}")


def delete_aux_files(folder_path):
    patterns = ["*.aux", "*.log", "*.tex"]  # Pattern to match files

    # Find and delete each matching file
    for pattern in patterns:
        for file_path in glob.glob(os.path.join(folder_path, pattern)):
            print(file_path)
            os.remove(file_path)
            print(f"{file_path} deleted successfully.")


if __name__ == "__main__":
    # Generate problems and create the LaTeX file
    ws_rows = 4
    ws_cols = 5

    pdf_destination = os.path.expanduser("~") + '/GitHub/DailyMath/Website/worksheets/'

    # Open the YAML config file
    with open('worksheets.yml', 'r') as file:
        # Load the contents of the file
        data = yaml.safe_load(file)

    for field in data:
        for topic in data[field]:
            for item in data[field][topic]:
                if 'worksheets' in item:
                    for worksheet in item['worksheets']:
                        problems = generate_problems([field, worksheet['constraint-type'], worksheet['constraint']], ws_rows, ws_cols, worksheet['largest-term'])
                        latex_table = create_latex(ws_rows, ws_cols, problems, field, worksheet['latex-description'])
                        base_name = worksheet['filename']
                        save_latex_file(latex_table, f'TeX/{base_name}.tex')
                        generate_pdf(f'TeX/{base_name}.tex')
                        source_path=f'TeX/{base_name}.pdf'
                        destination_path = pdf_destination + f'{base_name}.pdf'
                        shutil.move(source_path, destination_path)

    delete_aux_files('TeX')
