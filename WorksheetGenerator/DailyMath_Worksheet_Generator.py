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
import time

def generate_problems(p_type, constraints, rows, cols, num_terms):
    # Initialize variables
    new_problems = []
   
    terms = [0]*num_terms
 
    if p_type == 'subtraction':
        offset = 1
    else:
        offset = 0


    if p_type in ['addition','subtraction']:
        smallest = 1
    elif p_type == 'multiplication':
        smallest = 2

    if 'smallest term lower' in constraints:
        slb = constraints['smallest term lower']
    else:
        slb = smallest

    largest = constraints.get("largest-term")


    # Set lower bound on first term
    if 'largest term lower' in constraints:
        if p_type =='subtraction':
            flb = max(constraints['largest term lower'],slb+1)
        else:
            flb = constraints['largest term lower']  # Set the lower bound for the first term
    else:
        flb = 0


        #if any(c in constraint_dict for c in {'max', 'none', 'smallest term', 'difference', 'lower bound'}):
        #if (any(c["type"] in {'max', 'none', 'smallest term', 'difference', 'lower bound'} for c in constraints)):

    for _ in range(rows * cols):
        #Initialize variable to check for repeat neighbors.
        terms1 = terms.copy() # Make a new list terms1.  Note: settings terms1=terms only make a memory reference; it does not create a new variable

        while terms1 == terms:  # Ensure the same problem does not appear twice in a row
            
            # Get first term
            if 'max' in constraints:
                m = constraints['max']
                terms[0] = random.SystemRandom().randint(max(smallest+offset, flb), min(largest, m))
            else:
                terms[0] = random.SystemRandom().randint(max(flb, smallest+offset), largest)

            if 'smallest term' in constraints:
                if p_type =='subtraction':
                    sterm = min(constraints['smallest term'], terms[0]-1)
                else:
                    sterm = constraints['smallest term']
            else:
                if p_type == 'subtraction':
                    sterm = terms[0]-1
                else:
                    sterm = largest
            
            #Get next terms
            for i in range(1, num_terms):
                if 'difference' in constraints:
                    diff = constraints['difference']
                    if p_type == 'subtraction':
                        terms[i] = random.SystemRandom().randint(max(slb, terms[0] - diff), sterm)  # Ensures the difference is at most diff
                    else:
                        terms[i] = random.SystemRandom().randint(max(slb,terms[0]-diff), min(terms[0]+diff, largest))
                elif 'lower bound' in constraints:
                    lb = constraints['lower bound']
                    terms[i] = random.SystemRandom().randint(lb-terms[0], largest)
                elif 'max' in constraints:
                    terms[i] = random.SystemRandom().randint(slb, min(largest, m - sum(terms[0:i])-(num_terms-1-i)))  # Ensures sum is <= max_value
                else:
                    terms[i] = random.SystemRandom().randint(slb, sterm)
        
        new_problems.append(terms.copy())
       

    return new_problems


def create_latex(rows, cols, int_pairs, p_type, description, alg, logo, fname, num_terms, orientation):
    box_height = str(4/(5*rows))+ r"\textheight"
    box_width = str(1/cols)+ r"\textwidth"
    latex_content = r"""\documentclass{article}
\usepackage[fontsize=20pt]{fontsize}
\usepackage[letterpaper, margin=.8in]{geometry}
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
    x = [0]*num_terms
    for i in range(rows):

        for j in range(cols):
            x = int_pairs[cols*i+j].copy()

            latex_content = latex_content + '\\Block{ \n'
            if fname == 'm10':
                latex_content = latex_content + f'\[ {x[0]} + {x[1]} = 10 + \\fbox{{\\rule[-2ex]{{5ex}}{{0pt}}\\rule{{0pt}}{{3.5ex}}}} = \\fbox{{\\rule[-2ex]{{5ex}}{{0pt}}\\rule{{0pt}}{{3.5ex}}}} \] \n}}%\n'

            elif orientation == 'horizontal':
                if alg:  # Only setup for addition at moment
                    blank = random.randint(0, num_terms-1) # We will randomly choose which term is left blank
                    latex_content = latex_content + '\[ '
                    if blank == 0:
                        latex_content = latex_content + '\\fbox{\\rule[-2ex]{4ex}{0pt}\\rule{0pt}{3.5ex}} '
                    else:
                        latex_content = latex_content + f'{x[0]}'

                    for k in range(1,num_terms):
                        if blank == k:
                            latex_content = latex_content + ' + \\fbox{\\rule[-2ex]{4ex}{0pt}\\rule{0pt}{3.5ex}} '
                        else:
                            latex_content = latex_content + f'+ {x[k]} '

                    latex_content = latex_content + f' = {sum(x)} \] \n}}%\n'

                else:
                    latex_content = latex_content + f'\[ {x[0]} '
                    for k in range(1,num_terms):
                        if p_type == 'addition':
                            latex_content = latex_content + f'+ {x[k]} '
                        elif p_type == 'subtraction':
                            latex_content = latex_content + f'- {x[k]} '
                        elif p_type == 'multiplication':
                            latex_content = latex_content + f'\\times {x[k]} '
                    latex_content = latex_content + ' = \\fbox{\\rule[-2ex]{5ex}{0pt}\\rule{0pt}{3.5ex}} \] \n}%\n'

            else:

                if alg:
                    latex_content = latex_content + '\\vspace{-.75ex}\n'


                latex_content = (latex_content + 
                                   ('\\[ \n'
                                    '	\\begin{array}{l r}\n'))

                for k in range(num_terms-1):
                    latex_content = latex_content + f' & {x[k]} \\\\\n'

                if not alg:
                    if p_type == 'addition':
                        latex_content = latex_content + f'		+ 	& {x[num_terms-1]} \\\\\n'
                    elif p_type == 'multiplication':
                        latex_content = latex_content + f'		\\times 	& {x[num_terms-1]} \\\\\n'
                    elif p_type == 'subtraction':
                        latex_content = latex_content + f'		-	& {x[num_terms-1]} \\\\\n'

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
                                          f'            & {sum(x)} \Tstrut \\\\\n'))

                    elif p_type == 'subtraction':
                        latex_content = (latex_content +
                                         (f'		-	& \\fbox{{\\rule{{4ex}}{{0pt}}\\rule{{0pt}}{{5ex}}}}  \\\\\n'
                                          '             \hline\n'
                                          f'            & {x[0] - sum(x[1:num_terms-1])} \Tstrut \\\\\n'))

                    elif p_type == 'multiplication':
                        product = 1
                        for num in x:
                            product *= num
                        latex_content = (latex_content +
                                         (f'		\\times	& \\fbox{{\\rule{{4ex}}{{0pt}}\\rule{{0pt}}{{5ex}}}}  \\\\\n'
                                          '             \hline\n'
                                          f'            & {product} \Tstrut \\\\\n'))

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
                if 'number of terms' in worksheet:
                    ws_terms = worksheet['number of terms']
                else:
                    ws_terms = 2

                if 'orientation' in worksheet:
                    ws_orientation = worksheet['orientation']
                elif ws_terms > 2:
                    ws_orientation = 'horizontal'
                else:
                    ws_orientation = 'vertical'



                problems = generate_problems(problem_type, ws_constraints, ws_rows, ws_columns, ws_terms) # Generate the problems.
                content = create_latex(ws_rows, ws_columns, problems, problem_type, ws_description, is_algebra, logo_path, ws_filename, ws_terms, ws_orientation) # Take generated problems and write LaTeX file
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
