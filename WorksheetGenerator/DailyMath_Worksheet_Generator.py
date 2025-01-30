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

def generate_problems(p_type, constraints, rows, cols):
    # Initialize variables
    new_problems = []
    a = 0
    b = 0
    offset = 0

    if p_type in ['addition','subtraction']:
        smallest = 1

        if p_type == 'subtraction':
            offset = 1
        # largest = constraints.get("largest-term") - offset

    elif p_type == 'multiplication':
        smallest = 2
        # largest = constraints.get("largest-term")

    largest = constraints.get("largest-term")


    # Set lower bound on first term
    if 'largest term lower' in constraints:
        flb = constraints['largest term lower']  # Set the lower bound for the first term
    else:
        flb = 0


        #if any(c in constraint_dict for c in {'max', 'none', 'smallest term', 'difference', 'lower bound'}):
        #if (any(c["type"] in {'max', 'none', 'smallest term', 'difference', 'lower bound'} for c in constraints)):

    for _ in range(rows * cols):
        #Initialize variable to check for repeat neighbors.
        a1 = a
        b1 = b

        while a1 == a and b1 == b:  # Ensure the same problem does not appear twice in a row

            if 'max' in constraints:
                m = constraints['max']
                a = random.randint(max(smallest+offset, flb), min(largest, m))
                b = random.randint(smallest, min(largest, m - a))  # Ensures sum is <= max_value
            else:
                a = random.randint(max(flb, smallest+offset), largest)

            if 'smallest term' in constraints:
                if p_type =='subtraction':
                    sterm = min(constraints['smallest term'], a-1)
                else:
                    sterm = constraints['smallest term']
            else:
                if p_type == 'subtraction':
                    sterm = a-1
                else:
                    sterm = largest

            if 'difference' in constraints:
                diff = constraints['difference']
                if p_type == 'subtraction':
                    b = random.randint(max(smallest, a - diff), sterm)  # Ensures the difference is at most diff
                else:
                    b = random.randint(max(smallest,a-diff), min(a+diff, largest))
            elif 'lower bound' in constraints:
                lb = constraints['lower bound']
                b = random.randint(lb-a, largest)
            else:
                b = random.randint(smallest, sterm)

            new_problems.append((a, b))

        # if p_type in {'addition', 'multiplication'}:
        #     new_problems.append((a, b))
        # elif p_type == 'subtraction':
        #     new_problems.append((a+b, random.choice([a,b])))

    # elif p_type=='subtraction':
    #     for _ in range(rows * cols):
    #         a1 = a
    #         b1 = b
    #         while a1 == a and b1 == b: #Ensure the same problem does not appear twice in a row
    #             a = random.randint(max(flb,2), largest)
    #             if 'smallest term' in constraints:
    #                 sterm = constraints['smallest term']
    #                 b = random.randint(1, min(sterm,a - 1))  # Ensures the term being subtracted is at most p_info[2].
    #             elif 'difference' in constraints:
    #                 diff = constraints['difference']
    #                 b = random.randint(max(1, a - diff), a - 1)  # Ensures the difference is at most p_info[2]
    #         new_problems.append((a, b))

    return new_problems


def create_latex(rows, cols, int_pairs, p_type, description, alg, logo, fname):
    box_height = str(4/(5*rows))+ r"\textheight"
    box_width = str(1/cols)+ r"\textwidth"
    latex_content = r"""\documentclass{article}
\usepackage[fontsize=20pt]{fontsize}
\usepackage[letterpaper, margin=1in]{geometry}
\usepackage{graphicx}


\newcommand\Block[1]{%
\setlength\fboxsep{0pt}\setlength\fboxrule{0.1pt}% delete
\fbox{% delete
\begin{minipage}[c][""" + box_height+ '][t]{' + box_width + r"""}
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
            x = int_pairs[cols*i+j][0]
            y = int_pairs[cols*i+j][1]

            latex_content = latex_content + '\\Block{ \n'

            if fname == 'm10':
                latex_content = latex_content + f'\[ {x} + {y} = 10 + \\fbox{{\\rule[-2ex]{{5ex}}{{0pt}}\\rule{{0pt}}{{3.5ex}}}} = \\fbox{{\\rule[-2ex]{{5ex}}{{0pt}}\\rule{{0pt}}{{3.5ex}}}} \] \n}}%\n'

            else:

                if alg:
                    latex_content = latex_content + '\\vspace{-.75ex}\n'


                latex_content = (latex_content +
                                 (  '\\[ \n'
                                    '	\\begin{array}{l r}\n'
                                    f'			& {x} \\\\\n'))

                if not alg:
                    if p_type == 'addition':
                        latex_content = latex_content + f'		+ 	& {y} \\\\\n'
                    elif p_type == 'multiplication':
                        latex_content = latex_content + f'		\\times 	& {y} \\\\\n'
                    elif p_type == 'subtraction':
                        latex_content = latex_content + f'		-	& {y} \\\\\n'

                    latex_content = (latex_content +
                                     ('	    \hline\n'
                                      '	\end{array}\n'
                                      '\\]\n'
                                      '}%\n'))

                elif alg:

                    if p_type == 'addition':
                        latex_content = (latex_content +
                                         (f'		+	&  \\fbox{{\\rule{{4ex}}{{0pt}}\\rule{{0pt}}{{5ex}}}}  \\\\\n'
                                          '             \hline\n'
                                          f'            & {x + y} \Tstrut \\\\\n'))

                    elif p_type == 'subtraction':
                        latex_content = (latex_content +
                                         (f'		-	& \\fbox{{\\rule{{4ex}}{{0pt}}\\rule{{0pt}}{{5ex}}}}  \\\\\n'
                                          '             \hline\n'
                                          f'            & {x - y} \Tstrut \\\\\n'))

                    elif p_type == 'multiplication':
                        latex_content = (latex_content +
                                         (f'		\\times	& \\fbox{{\\rule{{4ex}}{{0pt}}\\rule{{0pt}}{{5ex}}}}  \\\\\n'
                                          '             \hline\n'
                                          f'            & {x * y} \Tstrut \\\\\n'))

                    latex_content = (latex_content +
                                     ('	\end{array}\n'
                                     '\\]\n'
                                     '}%\n'))

        if i < rows-1:
            latex_content = latex_content + r'\par\nointerlineskip\noindent'+'\n'

    latex_content = latex_content + r'\end{document}'
    return latex_content


def save_latex_file(content_to_write, filename):
    with open(filename, "w") as lfile:
        lfile.write(content_to_write)


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
            if 'algebra' in topic:
                is_algebra = topic['algebra']
            else:
                is_algebra = False

            for worksheet in topic['worksheets']: #Cycle through the worksheets in each sub-field
                
                ws_rows = worksheet['rows']
                ws_columns = worksheet['cols']
                ws_constraints = worksheet['constraints']
                ws_description = worksheet['latex-description']
                ws_filename = worksheet['filename']

                problems = generate_problems(problem_type, ws_constraints, ws_rows, ws_columns) # Generate the problems.
                content = create_latex(ws_rows, ws_columns, problems, problem_type, ws_description, is_algebra, logo_path, ws_filename) # Take generated problems and write LaTeX file
                ws_filename = worksheet['filename']
                save_latex_file(content, f'{ws_filename}.tex') # Save the LaTeX file
                try:
                    generate_pdf(f'{ws_filename}.tex') # Run LateX to generate pdf; requires TeX-Live install on system.
                except:
                    print(f'PDF generation of {ws_filename}.tex failed.  Check to make sure you have Tex Live installed.')
                    break
                source_path=f'{ws_filename}.pdf'
                destination_path = pdf_destination + f'{ws_filename}.pdf'
                shutil.move(source_path, destination_path) # Move pdfs to appropriate folder.

    try:
        delete_aux_files('') # Delete all the non-pdfs files generated during the process.
        print("=" * 60)
        print('Auxiliary files deleted successfully.')
    except:
        print("=" * 60)
        print('Deleting auxiliary files failed.')