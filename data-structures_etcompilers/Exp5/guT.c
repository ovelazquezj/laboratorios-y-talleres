/*
 * Editor de Texto Simple para WSL
 * Extensión de archivo: .gu
 * Compilar con: gcc guT.c -o guT -lncurses
 * Autor: Mtro Omar Velazquez
 * Licencia: Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)
 */

#include <locale.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ncurses.h>
#include <ctype.h>

#define MAX_LINES 1000
#define MAX_LINE_LENGTH 1024
#define CTRL_KEY(k) ((k) & 0x1f)

// Estructura para el buffer de texto
typedef struct {
    char lines[MAX_LINES][MAX_LINE_LENGTH];
    int num_lines;
    int cursor_x;
    int cursor_y;
    char filename[256];
    int modified;
} TextBuffer;

// Prototipos de funciones
void init_editor();
void cleanup_editor();
void draw_menu_bar();
void draw_status_bar(TextBuffer *buffer);
void draw_text(TextBuffer *buffer, int start_line);
void show_file_menu(TextBuffer *buffer);
void show_help_menu();
void new_file(TextBuffer *buffer);
void open_file(TextBuffer *buffer);
void save_file(TextBuffer *buffer);
void save_file_as(TextBuffer *buffer);
void insert_char(TextBuffer *buffer, char c);
void delete_char(TextBuffer *buffer);
void insert_newline(TextBuffer *buffer);
void move_cursor(TextBuffer *buffer, int direction);
void show_message(const char *message);
void get_string(const char *prompt, char *buffer, int max_len);

// Variables globales
WINDOW *main_win;
int screen_height, screen_width;

int main() {
    TextBuffer buffer = {0};
    buffer.num_lines = 1;
    strcpy(buffer.filename, "sin_titulo.gu");
    
    init_editor();
    
    int ch;
    int in_menu = 0;
    int running = 1;
    
    while (running) {
        draw_menu_bar();
        draw_text(&buffer, 0);
        draw_status_bar(&buffer);
        
        move(buffer.cursor_y + 2, buffer.cursor_x);
        refresh();
        
        ch = getch();
        
        switch(ch) {
            case CTRL_KEY('n'):  // Ctrl+N - Nuevo
                new_file(&buffer);
                break;
                
            case CTRL_KEY('o'):  // Ctrl+O - Abrir
                open_file(&buffer);
                break;
                
            case CTRL_KEY('s'):  // Ctrl+S - Guardar
                save_file(&buffer);
                break;
                
            case CTRL_KEY('a'):  // Ctrl+A - Guardar como
                save_file_as(&buffer);
                break;
                
            case CTRL_KEY('q'):  // Ctrl+Q - Salir
                if (buffer.modified) {
                    show_message("¿Guardar cambios? (s/n): ");
                    int save_ch = getch();
                    if (save_ch == 's' || save_ch == 'S') {
                        save_file(&buffer);
                    }
                }
                running = 0;
                break;
                
            case CTRL_KEY('g'):  // Ctrl+G - Ayuda
                show_help_menu();
                break;
                
            case KEY_F(1):  // F1 - Menú Archivo
                show_file_menu(&buffer);
                break;
                
            case KEY_F(2):  // F2 - Menú Ayuda
                show_help_menu();
                break;
                
            case KEY_UP:
                move_cursor(&buffer, 0);
                break;
                
            case KEY_DOWN:
                move_cursor(&buffer, 1);
                break;
                
            case KEY_LEFT:
                move_cursor(&buffer, 2);
                break;
                
            case KEY_RIGHT:
                move_cursor(&buffer, 3);
                break;
                
            case KEY_BACKSPACE:
            case 127:
            case 8:
                delete_char(&buffer);
                break;
                
            case '\n':
            case KEY_ENTER:
            case '\r':
                insert_newline(&buffer);
                break;
                
            default:
                if (isprint(ch)) {
                    insert_char(&buffer, ch);
                }
                break;
        }
    }
    
    cleanup_editor();
    return 0;
}

void init_editor() {
    setlocale(LC_ALL, "");
    initscr();
    raw();
    keypad(stdscr, TRUE);
    noecho();
    
    if (has_colors()) {
        start_color();
        init_pair(1, COLOR_WHITE, COLOR_BLUE);   // Menú
        init_pair(2, COLOR_BLACK, COLOR_WHITE);  // Status bar
        init_pair(3, COLOR_YELLOW, COLOR_BLACK); // Texto modificado
    }
    
    getmaxyx(stdscr, screen_height, screen_width);
}

void cleanup_editor() {
    endwin();
}

void draw_menu_bar() {
    attron(COLOR_PAIR(1));
    move(0, 0);
    for (int i = 0; i < screen_width; i++) {
        addch(' ');
    }
    move(0, 0);
    printw(" F1:Archivo  F2:Ayuda  | Ctrl+N:Nuevo  Ctrl+O:Abrir  Ctrl+S:Guardar  Ctrl+Q:Salir");
    attroff(COLOR_PAIR(1));
}

void draw_status_bar(TextBuffer *buffer) {
    attron(COLOR_PAIR(2));
    move(screen_height - 1, 0);
    for (int i = 0; i < screen_width; i++) addch(' ');
    move(screen_height - 1, 0);

    // Ajustar el tamaño del buffer a lo visible en pantalla
    int avail = (screen_width > 1) ? (screen_width - 1) : 1; // deja 1 col libre
    char status[/* VLA */ (size_t)avail + 1];

    snprintf(status, (size_t)avail + 1,
             " %s%s | Línea: %d/%d | Col: %d",
             buffer->filename,
             buffer->modified ? " [Modificado]" : "",
             buffer->cursor_y + 1,
             buffer->num_lines,
             buffer->cursor_x + 1);

    printw("%s", status);
    attroff(COLOR_PAIR(2));
}


void draw_text(TextBuffer *buffer, int start_line) {
    int max_display_lines = screen_height - 3;
    
    for (int i = 1; i < screen_height - 1; i++) {
        move(i, 0);
        clrtoeol();
    }
    
    for (int i = 0; i < max_display_lines && i + start_line < buffer->num_lines; i++) {
        move(i + 2, 0);
        printw("%s", buffer->lines[i + start_line]);
    }
}

void show_file_menu(TextBuffer *buffer) {
    const char *items[] = {
        "1. Nuevo        (Ctrl+N)",
        "2. Abrir        (Ctrl+O)",
        "3. Guardar      (Ctrl+S)",
        "4. Guardar como (Ctrl+A)",
        "5. Salir        (Ctrl+Q)"
    };
    int n = sizeof(items)/sizeof(items[0]);
    int selected = 0;

    int h = 10, w = 36, y = 5, x = 10;
    WINDOW *menu_win = newwin(h, w, y, x);
    keypad(menu_win, TRUE);             // ← habilita flechas/Enter

    while (1) {
        werase(menu_win);
        box(menu_win, 0, 0);
        mvwprintw(menu_win, 1, 2, "MENÚ ARCHIVO");
        mvwhline(menu_win, 2, 2, ACS_HLINE, w - 4);

        for (int i = 0; i < n; i++) {
            if (i == selected) wattron(menu_win, A_REVERSE);
            mvwprintw(menu_win, 3 + i, 2, "%s", items[i]);
            if (i == selected) wattroff(menu_win, A_REVERSE);
        }
        mvwprintw(menu_win, 3 + n, 2, "ESC para cerrar");
        wrefresh(menu_win);

        int ch = wgetch(menu_win);
        if (ch == 27) break;                       // ESC
        else if (ch == KEY_DOWN)  selected = (selected + 1) % n;                 // ↓ cíclico
        else if (ch == KEY_UP)    selected = (selected - 1 + n) % n;             // ↑ cíclico
        else if (ch == '\n' || ch == KEY_ENTER) {                                // Enter
            switch (selected) {
                case 0: new_file(buffer); break;
                case 1: open_file(buffer); break;
                case 2: save_file(buffer); break;
                case 3: save_file_as(buffer); break;
                case 4: /* salir (handled por Ctrl+Q fuera) */ break;
            }
            break;
        } else if (ch >= '1' && ch <= '5') {
            selected = ch - '1';   // también permite números
        }
    }
    delwin(menu_win);
    clear();
}



void show_help_menu() {
    WINDOW *help_win = newwin(15, 40, 5, 10);
    box(help_win, 0, 0);
    
    mvwprintw(help_win, 1, 2, "AYUDA - Editor de Texto .gu");
    mvwhline(help_win, 2, 2, ACS_HLINE, 40 - 4);
    mvwprintw(help_win, 3, 2, "ATAJOS DE TECLADO:");
    mvwprintw(help_win, 4, 2, "Ctrl+N    - Archivo nuevo");
    mvwprintw(help_win, 5, 2, "Ctrl+O    - Abrir archivo");
    mvwprintw(help_win, 6, 2, "Ctrl+S    - Guardar");
    mvwprintw(help_win, 7, 2, "Ctrl+A    - Guardar como");
    mvwprintw(help_win, 8, 2, "Ctrl+Q    - Salir");
    mvwprintw(help_win, 9, 2, "Flechas   - Mover cursor");
    mvwprintw(help_win, 10, 2, "Backspace - Borrar carácter");
    mvwprintw(help_win, 11, 2, "Enter     - Nueva línea");
    mvwprintw(help_win, 13, 2, "Presione cualquier tecla...");
    
    wrefresh(help_win);
    getch();
    delwin(help_win);
    clear();
}

void new_file(TextBuffer *buffer) {
    if (buffer->modified) {
        show_message("¿Guardar cambios actuales? (s/n): ");
        int ch = getch();
        if (ch == 's' || ch == 'S') {
            save_file(buffer);
        }
    }
    
    memset(buffer->lines, 0, sizeof(buffer->lines));
    buffer->num_lines = 1;
    buffer->cursor_x = 0;
    buffer->cursor_y = 0;
    strcpy(buffer->filename, "sin_titulo.gu");
    buffer->modified = 0;
    
    show_message("Nuevo archivo creado");
}

void open_file(TextBuffer *buffer) {
    char filename[256];
    get_string("Nombre del archivo: ", filename, 256);
    
    if (strlen(filename) == 0) return;
    
    // Agregar extensión .gu si no la tiene
    if (!strstr(filename, ".gu")) {
        strcat(filename, ".gu");
    }
    
    FILE *fp = fopen(filename, "r");
    if (fp == NULL) {
        show_message("Error al abrir el archivo");
        return;
    }
    
    memset(buffer->lines, 0, sizeof(buffer->lines));
    buffer->num_lines = 0;
    
    while (fgets(buffer->lines[buffer->num_lines], MAX_LINE_LENGTH, fp) != NULL) {
        // Eliminar salto de línea
        int len = strlen(buffer->lines[buffer->num_lines]);
        if (len > 0 && buffer->lines[buffer->num_lines][len-1] == '\n') {
            buffer->lines[buffer->num_lines][len-1] = '\0';
        }
        buffer->num_lines++;
        if (buffer->num_lines >= MAX_LINES) break;
    }
    
    if (buffer->num_lines == 0) {
        buffer->num_lines = 1;
    }
    
    fclose(fp);
    strcpy(buffer->filename, filename);
    buffer->modified = 0;
    buffer->cursor_x = 0;
    buffer->cursor_y = 0;
    
    show_message("Archivo abierto correctamente");
}

void save_file(TextBuffer *buffer) {
    if (strcmp(buffer->filename, "sin_titulo.gu") == 0) {
        save_file_as(buffer);
        return;
    }
    
    FILE *fp = fopen(buffer->filename, "w");
    if (fp == NULL) {
        show_message("Error al guardar el archivo");
        return;
    }
    
    for (int i = 0; i < buffer->num_lines; i++) {
        fprintf(fp, "%s\n", buffer->lines[i]);
    }
    
    fclose(fp);
    buffer->modified = 0;
    show_message("Archivo guardado correctamente");
}

void save_file_as(TextBuffer *buffer) {
    char filename[256];
    get_string("Guardar como: ", filename, 256);
    
    if (strlen(filename) == 0) return;
    
    // Agregar extensión .gu si no la tiene
    if (!strstr(filename, ".gu")) {
        strcat(filename, ".gu");
    }
    
    strcpy(buffer->filename, filename);
    save_file(buffer);
}

void insert_char(TextBuffer *buffer, char c) {
    if (buffer->cursor_y >= MAX_LINES) return;
    
    char *line = buffer->lines[buffer->cursor_y];
    int len = strlen(line);
    
    if (len >= MAX_LINE_LENGTH - 1) return;
    
    // Mover caracteres a la derecha
    for (int i = len; i >= buffer->cursor_x; i--) {
        line[i + 1] = line[i];
    }
    
    line[buffer->cursor_x] = c;
    buffer->cursor_x++;
    buffer->modified = 1;
}

void delete_char(TextBuffer *buffer) {
    if (buffer->cursor_x == 0 && buffer->cursor_y == 0) return;
    
    if (buffer->cursor_x == 0) {
        // Unir con la línea anterior
        if (buffer->cursor_y > 0) {
            int prev_len = strlen(buffer->lines[buffer->cursor_y - 1]);
            strcat(buffer->lines[buffer->cursor_y - 1], buffer->lines[buffer->cursor_y]);
            
            // Mover todas las líneas hacia arriba
            for (int i = buffer->cursor_y; i < buffer->num_lines - 1; i++) {
                strcpy(buffer->lines[i], buffer->lines[i + 1]);
            }
            
            buffer->num_lines--;
            buffer->cursor_y--;
            buffer->cursor_x = prev_len;
            buffer->modified = 1;
        }
    } else {
        char *line = buffer->lines[buffer->cursor_y];
        int len = strlen(line);
        
        for (int i = buffer->cursor_x - 1; i < len; i++) {
            line[i] = line[i + 1];
        }
        
        buffer->cursor_x--;
        buffer->modified = 1;
    }
}

void insert_newline(TextBuffer *buffer) {
    if (buffer->num_lines >= MAX_LINES - 1) return;
    
    // Mover líneas hacia abajo
    for (int i = buffer->num_lines; i > buffer->cursor_y; i--) {
        strcpy(buffer->lines[i], buffer->lines[i - 1]);
    }
    
    // Dividir la línea actual
    char *current_line = buffer->lines[buffer->cursor_y];
    char *next_line = buffer->lines[buffer->cursor_y + 1];
    
    strcpy(next_line, &current_line[buffer->cursor_x]);
    current_line[buffer->cursor_x] = '\0';
    
    buffer->num_lines++;
    buffer->cursor_y++;
    buffer->cursor_x = 0;
    buffer->modified = 1;
}

void move_cursor(TextBuffer *buffer, int direction) {
    switch(direction) {
        case 0:  // Arriba
            if (buffer->cursor_y > 0) {
                buffer->cursor_y--;
                int line_len = strlen(buffer->lines[buffer->cursor_y]);
                if (buffer->cursor_x > line_len) {
                    buffer->cursor_x = line_len;
                }
            }
            break;
            
        case 1:  // Abajo
            if (buffer->cursor_y < buffer->num_lines - 1) {
                buffer->cursor_y++;
                int line_len = strlen(buffer->lines[buffer->cursor_y]);
                if (buffer->cursor_x > line_len) {
                    buffer->cursor_x = line_len;
                }
            }
            break;
            
        case 2:  // Izquierda
            if (buffer->cursor_x > 0) {
                buffer->cursor_x--;
            } else if (buffer->cursor_y > 0) {
                buffer->cursor_y--;
                buffer->cursor_x = strlen(buffer->lines[buffer->cursor_y]);
            }
            break;
            
        case 3:  // Derecha
            if (buffer->cursor_x < strlen(buffer->lines[buffer->cursor_y])) {
                buffer->cursor_x++;
            } else if (buffer->cursor_y < buffer->num_lines - 1) {
                buffer->cursor_y++;
                buffer->cursor_x = 0;
            }
            break;
    }
}

void show_message(const char *message) {
    move(screen_height - 2, 0);
    clrtoeol();
    printw("%s", message);
    refresh();
}

void get_string(const char *prompt, char *buffer, int max_len) {
    echo();
    move(screen_height - 2, 0);
    clrtoeol();
    printw("%s", prompt);
    refresh();
    getnstr(buffer, max_len - 1);
    noecho();
    
    move(screen_height - 2, 0);
    clrtoeol();
}
