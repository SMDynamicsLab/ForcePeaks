pacman::p_load(tidyverse, patchwork, here, lme4, car, Routliers, ggdist)

# Asincronías ####
data_asyn <- read_csv(here("data/Df.csv")) |>
  mutate(Cond = fct_recode(Cond, 
                           "Finger" = "D1",
                           "Finger" = "D2",
                           "Wrist" = "M1",
                           "Wrist" = "M2"))
head(data_asyn)

# Seteo el tema de ggplot2
theme_set(theme_bw())
theme_update(strip.background =element_rect(color = "white", fill="white"),
             strip.text = element_text(size = 12),
             legend.position = "bottom")

## Asincronías por participante ####
sujeto <- 10

# Asincronía promedio por tap para las 4 condiciones
data_asyn |>
  filter(Subjs == sujeto) |>
  ggplot(aes(x = Tap,
             y = Asyns_c)) +
  stat_summary() + 
  labs(y = "Asynchrony (ms)")
  facet_wrap(Cond~Period)

# Asincronía promedio por tap para 1 condición
condicion <- "Finger"
data_asyn |>
  filter(Subjs == sujeto, Cond == condicion) |>
  ggplot(aes(x = Tap,
             y = Asyns_c,
             color = as.factor(Period)))+
  geom_point() + 
  geom_line() + 
  labs(y = "Asynchrony (ms)", color = "ISI") +
  scale_color_brewer(palette = "Dark2") +
  facet_wrap(.~Trial, labeller = label_both) 

# Promedio para todos los sujetos por condición
condicion <- "Finger"
data_asyn |>
  filter(Cond == condicion) |>
  ggplot(aes(x = Tap,
             y = Asyns_c)) +
  stat_summary(fun.data = mean_se) + 
  facet_wrap(.~Subjs, scales = "free_y", labeller = label_both) + 
  labs(y = "Asynchrony (ms)", color = "ISI") +
  scale_color_brewer(palette = "Dark2") 

## Outliers ####
# Hay muchas posibilidades para eliminar outliers, una sería asincronía a asoncronía
# Calculo el promedio de las asincronías por sujeto, condición y Trial
summary_asyn <- data_asyn |>
  group_by(Subjs, Cond, Trial, Period) |>
  summarise(m_asyn = mean(Asyns_c)) 
head(summary_asyn)

summary_asyn |>
  ggplot(aes(x = m_asyn)) +
  geom_histogram(fill = "steelblue") +
  facet_grid(Cond~Period)

# Acá abajo se hace todo el procedimiento de eliminar los outliers
summary_asyn_NO_outliers <- summary_asyn |> 
  group_by(Subjs, Cond, Period) |> 
  mutate(N = n()) |>
  filter(N>2) |>
  nest() |>
  mutate(inf = map_dbl(~ outliers_mad(.x$m_asyn, na.rm = T, threshold = 1.5)$LL_CI_MAD, .x = data),
         sup = map_dbl(~ outliers_mad(.x$m_asyn, na.rm = T, threshold = 1.5)$UL_CI_MAD, .x = data)) |>
  unnest(cols = c(data)) |>
  ungroup() |>
  rowwise() |>
  filter(between(m_asyn, inf, sup)) |>
  select(-c("inf", "sup"))

# El sujeto 2 tapeó a contratiempo, hay que sacarlo
data_asyn |>
  filter(Subjs == 2) |>
  ggplot(aes(x = Asyns_c)) +
  geom_histogram(fill = "steelblue") +
  facet_wrap(.~Cond)

summary_asyn_NO_outliers |> 
  filter(Subjs != 2) |> # hay que ver qué hacemos con este sujeto 2 que tiene una condición en la que 
  # las asincronías dan re positivas.
  ggplot(aes(x = Cond,
             y = m_asyn,
             group = Period)) +
  geom_hline(yintercept = 0, linetype = "dashed") +
  stat_interval(position = position_dodge(width = .4)) +
  scale_color_brewer() +
  theme_bw() 
# Hasta acá lo que pareceía es que hay un efecto de condición (trials con dedo con)
# asyns más negativas y del ISI, trials con 666 con asyns más negativas (esto tiene acuerdo)
# con la literatura (ver, por ejemplo, review de Repp).

# Filtro las asyn haciendo un inner_join
data_asyn_no_outliers <- data_asyn |> 
  inner_join(summary_asyn_NO_outliers |> select(c("Subjs", "Cond", "Period", "Trial"))) |>
  filter(Subjs != 2) 

## Distribución de las asincronías ####
data_asyn_no_outliers |>
  ggplot(aes(x = Asyns_c)) +
  geom_histogram(fill = "steelblue") +
  labs(x = "Asynchrony (ms)")

# Diferencia entre pico 1 y pico 2
data_asyn_no_outliers <- data_asyn_no_outliers |>
  mutate(dif_peaks = Asyns_p1 - Asyns_p2)

data_asyn_no_outliers |>
  ggplot(aes(x = Cond,
             y = dif_peaks)) +
  geom_jitter(color = "steelblue", alpha = .2) +
  labs(y = "Time difference between peaks (ms)", x = NULL) +
  scale_color_brewer(palette = "Dark2") + # Color
  scale_fill_brewer(palette = "Dark2") + # Fill
  stat_summary(size = 1) +
  theme_bw()

# La densidad general
data_asyn_no_outliers |>
  ggplot(aes(x = dif_peaks,
             color = Cond,
             fill = Cond)) +
  geom_density(alpha = .5) +
  scale_color_brewer(palette = "Dark2") + # Color
  scale_fill_brewer(palette = "Dark2") + # Fill
  labs(x = "Time difference between peaks (ms)", y = NULL,
       color = NULL, fill = NULL)

# La densidad por sujeto
data_asyn_no_outliers |>
  ggplot(aes(x = dif_peaks,
             color = Cond,
             fill = Cond)) +
  geom_density(alpha = .5) +
  facet_wrap(.~Subjs, scales = "free_y") +
  scale_color_brewer(palette = "Dark2") + # Color
  scale_fill_brewer(palette = "Dark2") + # Fill
  labs(x = "Time difference between peaks (ms)", y = NULL,
       color = NULL, fill = NULL)

## Asincronías vs. diferencia de picos ####

data_asyn_no_outliers |>
  ggplot(aes(x = dif_peaks,
             y = Asyns_p1)) +
  geom_point(aes(color = Cond),alpha = .2) +
  geom_smooth(method = "lm") +
  scale_color_brewer(palette = "Dark2") + # Color
  labs(x = "Time difference between peaks (ms)", y = NULL,
       color = NULL, fill = NULL)

# Fuerza ####
data_force <- read_csv(here("data/Df_Voltage.csv"))
data_force

data_force_idx <- data_force |>
  group_by(Cond, Block, Subjs, Trial, Tap) |>
  summarise()

data_force %>%
  filter(Block == 1, Subjs == 1, Trial == 5, Tap == 1) %>%
  ggplot(aes(x = Time,
             y = Voltages)) +
  geom_line(size = 2) + 
  facet_wrap(.~Cond) + 
  theme_bw()

## Figura fuerza promedio #### 
mean_subj_force <- data_force |>
  mutate(isi = case_when(
    Cond == "D1" ~ "444 ms",
    Cond == "D2" ~ "666 ms",
    Cond == "M1" ~ "444 ms",
    Cond == "M2" ~ "666 ms",
  ),
  Cond = fct_recode(Cond, 
                    "Finger" = "D1",
                    "Finger" = "D2",
                    "Wrist" = "M1",
                    "Wrist" = "M2")) |>
  group_by(Subjs, Cond, isi, Trial, Time) |>
  summarise(mVoltages = mean(Voltages)) |>
  group_by(Subjs, Cond, isi, Time) |>
  summarise(MVoltages = mean(mVoltages))
  
mean_cond_force <- mean_subj_force |>
  group_by(Cond, isi, Time) |>
  summarise(MVoltages = median(MVoltages))

mean_subj_force  |>
  ggplot(aes(x = Time,
             y = MVoltages, 
             color = Cond)) +
  geom_line(aes(group = paste(Subjs, Cond)), linewidth = 1, alpha = .1) + 
  geom_line(data = mean_cond_force, linewidth = 1.5) +
  labs(x = "Time (ms)", y = "Voltage (a.u.)", color = NULL) + 
  facet_wrap(.~isi) + 
  scale_color_brewer(palette = "Dark2") +
  theme_bw() +
  theme(strip.background =element_rect(color = "white", fill="white"),
        legend.position = "bottom")

## Figura esquemática ####
# Vamos a hacer el Tap 0 del Trial 0 del sujeto 4 (esto previa inspección visual)
sujeto <- 4

# Me quedo con las asincronías para plotear los movimientos
asyn_selected <- data_asyn |>
  filter(Subjs == sujeto, Cond %in% c("D1", "M1"), Trial == 0, Tap == 0) |>
  select(all_of(c("Cond", "Asyns_c", "Asyns_p1", "Asyns_p2")))

# Filtro las tramas de fuerza que me interesan
force_selected <- data_force |>
  filter(Subjs == sujeto, Cond %in% c("D1", "M1"), Trial == 0, Tap == 0) |>
  select(all_of(c("Cond", "Time", "Voltages"))) |> 
  filter(Voltages>0) |>
  left_join(asyn_selected) |> # Le pego el tibble con las asincronías
  mutate(`Aligned to peak 1` = Time - Asyns_p1 + Asyns_c, # Calculo un nuevo tiempo alineado a distintos picos
         `Aligned to peak 2` = Time - Asyns_p2 + Asyns_c) |>
  select(-c(Asyns_c, Time, Asyns_p1, Asyns_p2)) |>
  mutate(Cond = fct_recode(Cond, 
                           "Wrist" = "D1",
                           "Finger" = "M1"))

# Me queda:
head(force_selected)

# Lo paso a formato long para plotear todo de una
force_long <- force_selected |> 
  pivot_longer(cols = c(`Aligned to peak 1`, `Aligned to peak 2`), values_to = "time", names_to = "peak") 

# Me queda:
head(force_long)

# Armo tibble para el texto del estímulo
stim_label_tbl <- tibble(x = 0, y = 0, label = "Stimulus")

# Armo tibble para los textos de las asincronías
asyn_labels_tbl <- tibble(peak = c("Aligned to peak 1", "Aligned to peak 1", "Aligned to peak 2", "Aligned to peak 2"),
                          Cond = c("Wrist", "Finger", "Wrist", "Finger"),
                          label = c("Asyn. for wrist", "Asyn. for finger", "Asyn. for wrist", "Asyn. for finger"),
                          y = c(920, 860, 920, 860),
                          x = c(0, 0, 0, 0),
                          xmin = c(asyn_selected$Asyns_c-asyn_selected$Asyns_p1, asyn_selected$Asyns_c-asyn_selected$Asyns_p2))
force_long |>
  ggplot(aes(x = time,
             y = Voltages)) +
  geom_vline(xintercept = 0, linetype = "dashed") + # El cero
  geom_vline(data = asyn_labels_tbl, aes(xintercept = xmin, color = Cond), # Los contactos
             linetype = "dashed", show.legend = FALSE) +
  geom_segment(data = asyn_labels_tbl, aes(x = xmin, xend = x, y = y, yend = y, color = Cond), # Los segmentos que muestran la asincronía
               linewidth = 1) +
  geom_text(data = stim_label_tbl, aes(x = x, y = y, label = label), # El texto del estímulo
            hjust = -0.05, vjust = -0.5) +
  geom_text(data = asyn_labels_tbl, aes(x = x, y = y, label = paste0(label, ": ", xmin, " ms"), color = Cond), # El texto de las asincronías
            hjust = -0.05, vjust = 0.5, size = 4, show.legend = FALSE) +
  geom_line(aes(color = Cond), # Las trazas de fuerza
            linewidth = 1.5) +
  labs(x = "Time (ms)", y = "Voltage (a.u.)", color = NULL) + # Labels
  scale_color_brewer(palette = "Dark2") + # Color
  facet_grid(.~peak, scales = "free_x") + # Facet con eje x libre
  theme_bw() +
  theme(strip.background =element_rect(color = "white", fill="white"),
        strip.text = element_text(size = 12),
        legend.position = "bottom")

data_asyn |>
  filter(Subjs == sujeto, Cond %in% c("D1", "M1"), Trial == 0)
