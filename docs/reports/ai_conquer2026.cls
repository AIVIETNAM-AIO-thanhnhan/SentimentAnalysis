% =========================
% ai_conquer2026.cls  (AIVN Template)
% =========================
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{ai_conquer2026}[2026/04/17 AI Conquer 2026 template]

% Pass unknown options to article
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax
\LoadClass[12pt]{article}

% =========================================================
% I. LANGUAGE & FONT SETUP
% =========================================================
\PassOptionsToPackage{vietnamese.licr}{babel}
\RequirePackage[vietnamese=nohyphenation]{hyphsubst}
\RequirePackage[vietnamese]{babel}
\RequirePackage[T1]{fontenc}
\RequirePackage{lmodern,mathrsfs}
\RequirePackage[bottom]{footmisc}

% =========================================================
% II. BASIC PACKAGES
% =========================================================
\RequirePackage[table,dvipsnames]{xcolor}
\RequirePackage{ragged2e}
\RequirePackage{svg}
\RequirePackage{booktabs}
\RequirePackage{caption}
\RequirePackage{subcaption}
\RequirePackage{float}
\RequirePackage{amsmath,amssymb,amsfonts}
\RequirePackage{mathtools}
\RequirePackage{graphicx}
\RequirePackage{adjustbox}
\RequirePackage{multicol}
\RequirePackage[inline,shortlabels]{enumitem}
\RequirePackage{longtable}
\RequirePackage{setspace}
\RequirePackage{bm}
\RequirePackage{titling}
\RequirePackage{tabularx}
\RequirePackage{makecell}
\RequirePackage{xurl}
\RequirePackage{framed}
\RequirePackage{fancyhdr}
\RequirePackage{dirtree}
\RequirePackage{epigraph}
\RequirePackage{titlesec}
\RequirePackage{tocloft}

% =========================================================
% III. PAGE & TOC SETTINGS
% =========================================================
\setlength{\headheight}{14.5pt}
\setlength{\topmargin}{-.5in}
\setlength{\textheight}{9.25in}
\setlength{\oddsidemargin}{-0.1in}
\setlength{\textwidth}{6.8in}

\renewcommand{\cfttoctitlefont}{\Huge\bfseries}
\setlength{\cftaftertoctitleskip}{2em}
\setlength{\cftbeforesubsecskip}{7pt}
\renewcommand{\cftsecleader}{\cftdotfill{\cftdotsep}}
\setlength{\cftsecnumwidth}{3em}
\renewcommand{\cftsecaftersnum}{\quad}
\setlength{\cftsubsecnumwidth}{4em}
\renewcommand{\cftsubsecaftersnum}{\quad}
\setlength{\cftsubsubsecnumwidth}{5em}
\renewcommand{\cftsubsubsecaftersnum}{\quad}

% =========================================================
% IV. BIBLIOGRAPHY & APPENDIX
% =========================================================
\RequirePackage[
    backend=bibtex,
    style=ieee,
    maxnames=1,
    minnames=1,
    uniquelist=false,
    hyperref=false
]{biblatex}

\DefineBibliographyStrings{english}{andothers = {et\addabbrvspace al\adddot}}
\AtBeginBibliography{\selectlanguage{english}}
\AtBeginDocument{\renewcommand\refname{}}

\RequirePackage[toc,page]{appendix}
\renewcommand{\appendixtocname}{Phụ lục}
\renewcommand{\appendixpagename}{Phụ lục}

% =========================================================
% V. HYPERLINKS & UTILITIES
% =========================================================
\RequirePackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=black,
    filecolor=magenta,
    citecolor=black,
    urlcolor=blue,
    pdfborder={0 0 0}, % tắt border (an toàn)
    pdftitle={AIO2025 Material},
    pdfpagemode=FullScreen
}

\RequirePackage[os=win]{menukeys}

% =========================================================
% VI. GLOBAL STYLE ADJUSTMENTS
% =========================================================
\setlength{\parskip}{0.5em}
\setlength{\parindent}{0pt}

% =========================================================
% VIII. COLORS (palette)
% =========================================================
\definecolor{aivnGreen}{RGB}{52,79,30}
\definecolor{captiongray}{gray}{0.15}
\definecolor{captionbg}{RGB}{242,255,242}
\definecolor{watchoutbg}{RGB}{255,245,230}
\definecolor{watchoutborder}{RGB}{255,140,0}

\definecolor{codebackground}{RGB}{250,250,250}
\definecolor{codecomment}{RGB}{34,139,34}
\definecolor{codekeyword}{RGB}{0,0,255}
\definecolor{codestring}{RGB}{255,0,0}
\definecolor{codeidentifier}{RGB}{0,0,0}
\definecolor{codelinenumbers}{RGB}{90,90,90}

\definecolor{codegreen}{rgb}{0,0.6,0}
\definecolor{codegray}{rgb}{0.5,0.5,0.5}
\definecolor{codepurple}{rgb}{0.58,0,0.82}
\definecolor{backcolour}{rgb}{0.95,0.95,0.92}

% =========================================================
% IX. CODE LISTINGS & BOXES
% =========================================================
\RequirePackage{iftex}
\IfFileExists{vipythonhighlight.sty}{\RequirePackage{vipythonhighlight}}{}
\RequirePackage{listings}
\IfFileExists{tvietlistings.sty}{\RequirePackage{tvietlistings}}{}
\RequirePackage[most]{tcolorbox}
\tcbuselibrary{listings,skins,breakable}

% Font for cmd blocks
\ifLuaTeX
  \RequirePackage{fontspec}
  \newfontfamily\cmdmono{Consolas}
\else\ifXeTeX
  \RequirePackage{fontspec}
  \newfontfamily\cmdmono{Consolas}
\else
  \newcommand{\cmdmono}{\ttfamily}
\fi\fi

\definecolor{crtgreen}{rgb}{0.0,0.85,0.2}

\lstdefinestyle{aivnoutputstyle}{
  basicstyle=\ttfamily\footnotesize\color{black!85},
  commentstyle=\color{black!60},
  stringstyle=\color{black!70},
  breaklines=true,
  keepspaces=true,
  showstringspaces=false,
  columns=fullflexible,
}

\newtcblisting{aivnoutputbox}[1][]{%
  enhanced, breakable,
  listing engine=listings, listing only,
  colback=white, colframe=aivnGreen, coltext=black!85,
  coltitle=white, title={#1}, fonttitle=\bfseries\sffamily,
  left=6pt,right=6pt,top=6pt,bottom=6pt, arc=2mm, boxrule=0.4pt,
  listing options={style=aivnoutputstyle, numbers=none}
}

\newtcolorbox{aivncodebox}[1][]{%
  enhanced, breakable,
  colback=gray!10, colframe=aivnGreen,
  coltitle=white, colbacktitle=aivnGreen,
  title=#1, fonttitle=\bfseries\sffamily,
  listing only,
  listing engine=listings,
  listing options={
    language=Python,
    basicstyle=\ttfamily\footnotesize,
    commentstyle=\color{ForestGreen},
    keywordstyle=\color{blue},
    stringstyle=\color{red!70!black},
    numbers=left,
    numberstyle=\tiny\color{gray},
    numbersep=5pt,
    breaklines=true,
    xleftmargin=1.5em,
    framexleftmargin=1.5em
  }
}

% =========================================================
% X. CUSTOM BOXES & CAPTIONS
% =========================================================
\newtcolorbox{captionbelowboxaivn}{
  colback=aivnGreen,
  colframe=aivnGreen,
  boxrule=0pt, arc=4pt,
  left=4pt, right=4pt, top=2pt, bottom=2pt,
  width=\linewidth,
  halign=center,
  fontupper=\color{white}
}

\newcounter{hinh}
\newcommand{\capfig}[1]{%
  \refstepcounter{hinh}%
    Hình~\thehinh:~#1
}

\newtcolorbox{figurecardcaptionaivn}{
  colback=aivnGreen,
  colframe=aivnGreen,
  boxrule=0pt, arc=2pt,
  top=3pt, bottom=3pt, left=10pt, right=10pt,
  width=\linewidth,
  fontupper=\small\fontsize{11pt}{13pt}\selectfont\color{white}
}

\newtcolorbox{figurecaptionmodern}{
  colback=captionbg,
  colframe=aivnGreen,
  boxrule=1.5pt, bottomrule=2pt,
  left=6pt, right=6pt, top=4pt, bottom=2pt,
  width=\linewidth,
  fontupper=\small\fontsize{11pt}{13pt}\selectfont\color{black},
  halign=center
}

\newcounter{bang}
\newcommand{\captable}[1]{%
  \refstepcounter{bang}%
  Bảng~\thebang:~#1
}

\newtcolorbox{minisummaryboxaivn}{
  colback=captionbg!60,
  colframe=aivnGreen,
  arc=2pt,
  boxrule=0.6pt,
  left=6pt, right=6pt, top=4pt, bottom=4pt,
  fontupper=\small,
  width=\linewidth
}

% notebox needs fontawesome5
\IfFileExists{fontawesome5.sty}{\RequirePackage{fontawesome5}}{%
  % fallback nếu thiếu fontawesome5
  \newcommand{\faInfoCircle}{i}
}

\newtcolorbox{notebox}[2][]{enhanced,breakable,
  colback=gray!50!white,
  colframe=aivnGreen,
  fonttitle=\bfseries,
  title={\faInfoCircle\;Chú thích: #2},
  boxrule=0.8pt, arc=3pt,
  left=1mm, right=1mm, top=1mm, bottom=1mm,
  #1}

% =========================================================
% XI. COUNTERS, MATH, TITLE FORMAT, LOGO
% =========================================================
\newcounter{mycounter}
\newcommand\showmycounter{\stepcounter{mycounter}\themycounter}
\newcounter{hinh}

\DeclareMathOperator*{\argmax}{arg\,max}
\DeclareMathOperator*{\argmin}{arg\,min}
\DeclareMathOperator{\E}{\mathbb{E}}

\renewcommand{\thesection}{\Roman{section}.}
\renewcommand{\thesubsection}{\thesection\arabic{subsection}.}
\renewcommand{\thesubsubsection}{\thesubsection\arabic{subsubsection}.}

\titleformat{\section}{\normalfont\Huge\bfseries}{\thesection}{1em}{}
\titleformat{\subsection}{\normalfont\Large\bfseries}{\thesubsection}{1em}{}
\titleformat{\subsubsection}{\normalfont\normalsize\bfseries}{\thesubsubsection}{1em}{}

\titlespacing*{\section}{0pt}{1.2ex plus .2ex minus .2ex}{0.75ex}
\titlespacing*{\subsection}{0pt}{0.8ex plus .2ex minus .2ex}{0.5ex}
\titlespacing*{\subsubsection}{0pt}{0.6ex plus .2ex minus .2ex}{0.4ex}

% AIVN Logo
\newcommand{\AIVNLogoPath}{Figures/logo.pdf}
\newcommand{\AIVNSetLogo}[1]{\renewcommand{\AIVNLogoPath}{#1}}

\setlength{\droptitle}{-8em}
\pretitle{%
  \begin{flushleft}
    \includegraphics[height=2.0cm]{\AIVNLogoPath}\par
  \end{flushleft}
}
\posttitle{}