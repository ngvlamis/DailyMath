"""
    DailyMath Worksheet Generator
    This script generates all the worksheets on the website DailyMath.education.
    Copyright (C) 2024  Nicholas G. Vlamis

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

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


def create_latex(rows, cols, int_pairs, p_type, description, alg, logo):
    latex_content = r"""\documentclass{article}
\usepackage[fontsize=20pt]{fontsize}
\usepackage[letterpaper, margin=1in]{geometry}
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

\newcommand\Tstrut{\rule{0pt}{2.6ex}}         % = `top' strut
\newcommand\Bstrut{\rule[-2ex]{0pt}{0pt}}   % = `bottom' strut

\begin{document}

\pagenumbering{gobble}

\noindent
\begin{minipage}[t]{1.3cm}
\includegraphics[scale=0.1]{""" + logo + r"""}
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
            latex_content = latex_content + '\\Block{ \n'
            if not alg:
                latex_content = (latex_content +
                                 (  '\\[ \n'
                                    '	\\begin{array}{l r}\n'
                                    f'			& {x} \\\\\n'))
            elif alg:
                latex_content = (latex_content +
                                (   '\\vspace{-.75ex}\n'
                                    '\\[ \n'
                                    '	\\begin{array}{l r}\n'
                                    f'			& {x} \\\\\n'))


            if p_type == 'addition' and not alg:
                latex_content = latex_content + f'		+ 	& {y} \\\\\n'
            elif p_type == 'addition' and alg:
                latex_content = (latex_content +
                                 (f'		+	&  \\fbox{{\\rule{{4ex}}{{0pt}}\\rule{{0pt}}{{5ex}}}}  \\\\\n'
                                  '             \hline\n'
                                  f'            & {x + y} \Tstrut \\\\\n'
                                  '	\end{array}\n'
                                  '\\]\n'
                                  '}%\n'))
            elif p_type == 'subtraction' and not alg:
                latex_content = latex_content + f'		-	& {y} \\\\\n'
            elif p_type == 'subtraction' and alg:
                latex_content = (latex_content +
                                 (f'		-	& \\gobble{{{y}}} \\\\\n'
                                  '             \hline\n'
                                  f'            & {x - y} \Tstrut \\\\\n'
                                  '	\end{array}\n'
                                  '\\]\n'
                                  '}%\n'))
            if not alg:
                latex_content = (latex_content +
                             ('	    \hline\n'
                              '	\end{array}\n'
                              '\\]\n'
                              '}%\n'))

        if i < rows-1:
            latex_content = latex_content + r'\par\nointerlineskip\noindent'+'\n'

    latex_content = latex_content + r'\end{document}'
    return latex_content


def save_latex_file(content, filename):
    with open(filename, "w") as lfile:
        lfile.write(content)


def generate_pdf(tex_file_path):
    tex_file_name = os.path.basename(tex_file_path)
    print("=" * 60)
    print(f'Generating PDF from {tex_file_path}')
    subprocess.run(["pdflatex", "-interaction=batchmode", tex_file_name], check=True)


def delete_aux_files(folder_path):
    patterns = ["*.aux", "*.log", "*.tex"]  # Pattern to match files

    # Find and delete each matching file
    for pattern in patterns:
        for file_path in glob.glob(os.path.join(folder_path, pattern)):
            os.remove(file_path)
            # print(f"{file_path} deleted successfully.")


if __name__ == "__main__":

    # Generate pdf worksheets based on config file.

    # Set the number of columns and rows for the worksheet.
    ws_rows = 4
    ws_cols = 5

    # Set default paths
    current_directory = os.getcwd() # Get the current working directory
    project_directory = os.path.abspath(os.path.join(current_directory, "..")) # Go one step back to the parent directory
    ws_yaml_path =  os.path.join(project_directory,'WebsiteGenerator/_data/worksheets.yml') # Path of config file for worksheets
    pdf_destination = os.path.join(project_directory,'worksheets/') # Path of worksheets
    logo_path = os.path.join(project_directory, 'WebsiteGenerator/assets/img/cat-abacus.png') # Path of DailyMath logo

    # Open the YAML config file
    with open(ws_yaml_path, 'r') as file:
        # Load the contents of the file
        config = yaml.safe_load(file)

    # Cycle through all the worksheets in the config file, generating the pdfs.
    for field in config: #Cylce through the types of problems, e.g., addition, subtraction, etc.
        problem_type = str.lower(field['problem-type']) #Record the type of problem.
        for topic in field['subtype']: # Cycle through the sub-fields, e.g., single digit addition.
            is_algebra = topic['algebra']
            print(is_algebra)
            for worksheet in topic['worksheets']: #Cycle through the worksheets in each sub-field
                problems = generate_problems([problem_type, worksheet['constraint-type'], worksheet['constraint']], ws_rows,
                                             ws_cols, worksheet['largest-term']) # Generate the problems.
                latex_content = create_latex(ws_rows, ws_cols, problems, problem_type, worksheet['latex-description'], is_algebra, logo_path) # Take generated problems and write LaTeX file
                base_name = worksheet['filename']
                save_latex_file(latex_content, f'{base_name}.tex') # Save the LaTeX file
                try:
                    generate_pdf(f'{base_name}.tex') # Run LateX to generate pdf; requires TeX-Live install on system.
                except:
                    print(f'PDF generation of {base_name}.tex failed.  Check to make sure you have Tex Live installed.')
                    break
                source_path=f'{base_name}.pdf'
                destination_path = pdf_destination + f'{base_name}.pdf'
                shutil.move(source_path, destination_path) # Move pdfs to appropriate folder.

    try:
        delete_aux_files('') # Delete all the non-pdfs files generated during the process.
        print("=" * 60)
        print('Auxiliary files deleted successfully.')
    except:
        print("=" * 60)
        print('Deleting auxiliary files failed.')