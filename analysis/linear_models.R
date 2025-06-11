pacman::p_load(tidyverse, lme4, broom, modelsummary, patchwork, here, modelr, wesanderson)

# Acá están los datos de todas las versiones del experimento
data <- read_csv(here("data", "Df_2025.csv")) %>%
  filter(!(Subjs %in% c(2, 20, 26))) %>%
  # Sujetos 37 y 28 los sacamos porque están a contrafase
  select(- `...1`) %>%
  mutate(Effector = if_else(Effector == "D", "Finger", "Wrist"),
         Period = paste(Period, "ms"),
         Feedback = if_else(Subjs <= 26, "Feedback", "No Feedback")) 
datasummary_skim(data)

limits <- data %>%
  group_by(Effector, Period) %>%
  summarise(lower_bound = quantile(Asyns_c, .25) - 1.5 * IQR(Asyns_c),
            upper_bound = quantile(Asyns_c, .75) + 1.5 * IQR(Asyns_c))
limits

data <- data %>%
  left_join(limits)

data_no_outliers <- data %>%
  group_by(Subjs, Cond, Trial) %>%
  mutate(proportion = sum(Asyns_c < lower_bound | Asyns_c > upper_bound) / n()) %>%
  ungroup() %>%
  filter(proportion < 2/3) %>%
  select(-lower_bound, -upper_bound, -proportion)

# Código para ver los sujetos que están a contrafase
data %>% filter(Asyns_c < -200) %>%
  ggplot(aes(x = Peak_interval, y = Asyns_c, color = factor(Subjs))) +
  geom_point(alpha = .2) +
  geom_line(aes(group = interaction(Subjs, Trial))) +
  facet_wrap(Effector~Period) +
  theme_minimal() +
  theme_bw() +
  theme(legend.position = "top",
        strip.background = element_blank())

count_contrafase <- data %>% 
  group_by(Subjs, Cond, Trial) %>%
  mutate(nTaps = n(),
         m_asyn = mean(Asyns_c)) %>%
  filter(Asyns_c < -200) %>%
  group_by(Subjs, Cond, Trial, Period) %>%
  summarise(count = n(),
            nTaps = first(nTaps),
            m_asyn = first(m_asyn),
            prop = count/nTaps) %>%
  arrange(desc(count))

# Detección de outliers
# Nivel asincronía: Eliminar asincronías usando algún método de detección de outliers. 
# Tukeys fences (cuartiles e intervalo intercuartil).
data_no_outliers <- data_no_outliers %>%
  group_by(Subjs, Cond, Trial) %>%
  mutate(Q1 = quantile(Asyns_c, 0.25),
         Q3 = quantile(Asyns_c, 0.75),
         IQR = Q3 - Q1,
         lower_bound = Q1 - 1.5 * IQR,
         upper_bound = Q3 + 1.5 * IQR) %>%
  filter(Asyns_c >= lower_bound & Asyns_c <= upper_bound) %>%
  select(-Q1, -Q3, -IQR, -lower_bound, -upper_bound) %>%
  ungroup()

# Nivel trial: Considerar la condición de que el número de taps por trial sea mayor o igual a 4.
data_no_outliers_summ <- data_no_outliers %>%
  group_by(Subjs, Effector, Cond, Trial) %>%
  summarise(m_Asyn_c = mean(Asyns_c)) %>%
  group_by(Subjs, Effector) %>%
  mutate(Q1 = quantile(m_Asyn_c, 0.25),
         Q3 = quantile(m_Asyn_c, 0.75),
         IQR = Q3 - Q1,
         lower_bound = Q1 - 1.5 * IQR,
         upper_bound = Q3 + 1.5 * IQR) %>%
  filter(m_Asyn_c <= lower_bound | m_Asyn_c >= upper_bound) %>%
  select(-Q1, -Q3, -IQR, -lower_bound, -upper_bound) %>%
  ungroup()

data_no_outliers <- data_no_outliers %>%
  anti_join(data_no_outliers_summ, by = c("Subjs", "Effector", "Cond", "Trial"))

# Ahora sacamos los trials con menos de 4 taps
# data_no_outliers <- data_no_outliers %>%
#   group_by(Subjs, Cond, Trial) %>%
#   mutate(nTaps = n()) %>%
#   filter(nTaps >= 4) %>%
#   ungroup() %>%
#   select(-nTaps)

# Lo primero que tenemos que hacer es mostrar que hay una diferencia sistemática entre los picos 
# para ambos efectores, y que esta diferencia es consistente a lo largo de los periodos.
data_no_outliers %>% ggplot(aes(x = Effector, 
                    y = Peak_interval,
                    color = Effector)) +
  geom_jitter(alpha = .1, width = .1) +
  geom_boxplot(alpha = 0, width = .4) +
  stat_summary(size = 1, color = "darkgreen") +
  facet_wrap(.~Period, labeller = label_both) +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  labs(x = NULL,
       y = "Difference between force peaks (ms)",
       color = NULL) +
  theme_bw() +
  theme(legend.position = "top",
        strip.background = element_blank())

# Ahora quiero ver la densidad estimada de la variable Peak_interval para cada efector y periodo
data_no_outliers %>% 
  ggplot(aes(x = Peak_interval, fill = Effector)) +
  geom_density(alpha = .2) +
  scale_fill_manual(values = c("#0072B2", "#D55E00")) +
  labs(x = "Difference between force peaks (ms)",
       y = "Density",
       fill = NULL) +
  theme_bw() +
  theme(legend.position = "top",
        strip.background = element_blank())

# Calculemos el promdio de Peak?_interval por sujeto y effector
data_no_outliers %>%
  group_by(Subjs, Effector) %>%
  summarise(m_Peak_interval = mean(Peak_interval)) %>%
  ggplot(aes(x = Effector, y = m_Peak_interval, color = Effector)) +
  geom_point() +
  facet_wrap(~Subjs, labeller = label_both) +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  labs(x = NULL,
       y = "Difference between force peaks (ms)",
       color = NULL) +
  theme_bw() +
  theme(legend.position = "top",
        strip.background = element_blank())

# Ahora veamos que pinta tiene esto.
data_no_outliers %>% ggplot(aes(x = Peak_interval, y = Asyns_c)) +
  geom_point(aes(color = Effector), alpha = .2) +
  geom_smooth(method = "lm", se = FALSE, color = "darkgreen") +
  geom_abline(intercept = 0, slope = 0, linetype = "dashed") +
  facet_grid(Effector~Period) +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  theme_minimal() +
  theme_bw() +
  theme(legend.position = "top",
        strip.background = element_blank())

# Vamos a ajustar un modelo a los datos por tap pero excluyendo taps con asincronías mayores a +100ms
# Una cosa que tendríamos que mirar es cómo sacamos esos outliers de una forma más informada.
model <- lmer(data = data_no_outliers,
              Asyns_c ~ Peak_interval * Period * Feedback + (1|Subjs/Trial))
performance::check_model(model)

# Ahora hagamos los promeido por trial y de nuevo saquemos asincronías mayores a +50ms
data_summ <- data_no_outliers %>%
  group_by(Subjs, Period, Cond, Trial, Effector, Feedback) %>%
  summarise(m_Asyn_c = mean(Asyns_c),
            Peak_interval = mean(Peak_interval))

model_summ <- lmer(data = data_summ,
                   m_Asyn_c ~ Peak_interval * Period * Feedback + (1|Subjs))
performance::check_model(model_summ)

# Comparemos los modelos
models <- list("Model over taps" = model, 
               "Model over trials" = model_summ)

modelsummary(models,
             estimate  = "{estimate} [{conf.low}, {conf.high}]",
             statistic = "({p.value})",
             coef_omit = "Intercept", gof_map = NA)

# Podemos ver los resultados de los modelos
b <- list(geom_vline(xintercept = 0, color = 'orange'))

modelplot(models, background = b) +
  labs(x = 'Coefficients', 
       y = 'Term names') +
  aes(linetype = ifelse(p.value < 0.05, "Significant", "Not significant")) +
  scale_color_manual(values = wes_palette('Darjeeling1'))

data_summ <- data_summ %>%
  add_predictions(model_summ)

data_summ %>% ggplot(aes(x = Peak_interval, y = m_Asyn_c)) +
  geom_line(aes(y = pred, group = Subjs)) +
  geom_abline(intercept = 0, slope = 0, linetype = "dashed") +
  facet_grid(Feedback~Period) +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  theme_minimal()

# Miremos los datos sin feedback auditivo ####
data_summ_no_feedback <- data_summ %>%
  filter(Feedback == "No Feedback") 

m_Asyn_c <- data_summ_no_feedback %>%
  group_by(Period) %>%
  summarise(m_Asyn_c = mean(m_Asyn_c))

data_summ_no_feedback %>%
  ggplot(aes(x = Peak_interval, y = m_Asyn_c)) +
  geom_point(aes(color = Effector), alpha = .2) +
  geom_smooth(method = "lm", color = "black") +
  geom_abline(intercept = 0, slope = 0, linetype = "dashed") +
  geom_abline(data = m_Asyn_c, aes(intercept = m_Asyn_c, slope = 0),
              linetype = "dashed", color = "darkgreen") +
  geom_abline(data = m_Asyn_c, aes(intercept = m_Asyn_c, slope = -1),
              linetype = "dashed", color = "darkgreen") +
  facet_wrap(.~Period) +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  theme_minimal() +
  theme(legend.position = "top",
        strip.background = element_blank())

data_summ_no_feedback %>%
  ggplot(aes(x = Peak_interval, y = m_Asyn_c)) +
  geom_point(aes(color = Effector), alpha = .2) +
  geom_smooth(method = "lm", color = "black") +
  geom_abline(intercept = 0, slope = 0, linetype = "dashed") +
  geom_abline(intercept = mean(data_summ_no_feedback$m_Asyn_c), slope = 0,
              linetype = "dashed", color = "darkgreen") +
  geom_abline(intercept = mean(data_summ_no_feedback$m_Asyn_c), slope = -1,
              linetype = "dashed", color = "darkgreen") +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  theme_minimal() +
  theme(legend.position = "top",
        strip.background = element_blank())

# Ajustemos un modelo
model_no_feedback <- lmer(data = data_summ_no_feedback,
                   m_Asyn_c ~ Peak_interval * Period + (1|Subjs))
performance::check_model(model_no_feedback)

# Miremos lo mismo pero en los datos con feedback auditivo ####
data_summ_feedback <- data_summ %>%
  filter(Feedback == "Feedback")

m_Asyn_c <- data_summ_feedback %>%
  group_by(Period) %>%
  summarise(m_Asyn_c = mean(m_Asyn_c))

data_summ_feedback %>%
  ggplot(aes(x = Peak_interval, y = m_Asyn_c)) +
  geom_point(aes(color = Effector), alpha = .2) +
  geom_smooth(method = "lm", color = "black") +
  geom_abline(intercept = 0, slope = 0, linetype = "dashed") +
  geom_abline(data = m_Asyn_c, aes(intercept = m_Asyn_c, slope = 0),
              linetype = "dashed", color = "darkgreen") +
  geom_abline(data = m_Asyn_c, aes(intercept = m_Asyn_c, slope = -1),
              linetype = "dashed", color = "darkgreen") +
  facet_wrap(.~Period) +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  theme_minimal() +
  theme(legend.position = "top",
        strip.background = element_blank())

data_summ_feedback %>%
  ggplot(aes(x = Peak_interval, y = m_Asyn_c)) +
  geom_point(aes(color = Effector), alpha = .2) +
  geom_smooth(method = "lm", color = "black") +
  geom_abline(intercept = 0, slope = 0, linetype = "dashed") +
  geom_abline(intercept = mean(data_summ_feedback$m_Asyn_c), slope = 0,
              linetype = "dashed", color = "darkgreen") +
  geom_abline(intercept = mean(data_summ_feedback$m_Asyn_c), slope = -1,
              linetype = "dashed", color = "darkgreen") +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  theme_minimal() +
  theme(legend.position = "top",
        strip.background = element_blank())

# Ajustemos un modelo
model_feedback <- lmer(data = data_summ_feedback,
                          m_Asyn_c ~ Peak_interval * Period + (1|Subjs))
performance::check_model(model_feedback)

# Comparemos ambos modelos ####
models <- list("Model with feedback" = model_feedback, 
               "Model without feedback" = model_no_feedback)

modelsummary(models,
             estimate  = "{estimate} [{conf.low}, {conf.high}]",
             statistic = "({p.value})",
             coef_omit = "Intercept", gof_map = NA)

b <- list(geom_vline(xintercept = 0, color = 'orange'))

modelplot(models, background = b) +
  labs(x = 'Coefficients', 
       y = 'Term names') +
  aes(linetype = ifelse(p.value < 0.05, "Significant", "Not significant")) +
  scale_color_manual(values = wes_palette('Darjeeling1'))

m_Asyn_c <- data_summ %>%
  group_by(Period, Feedback) %>%
  summarise(m_Asyn_c = mean(m_Asyn_c))

data_summ %>% ggplot(aes(x = Peak_interval, y = m_Asyn_c)) +
  geom_point(aes(color = Effector), alpha = .2) +
  geom_smooth(method = "lm", color = "black") +
  geom_abline(intercept = 0, slope = 0, linetype = "dashed") +
  geom_abline(data = m_Asyn_c, aes(intercept = m_Asyn_c, slope = 0),
              linetype = "dashed", color = "darkgreen") +
  geom_abline(data = m_Asyn_c, aes(intercept = m_Asyn_c, slope = -1),
              linetype = "dashed", color = "darkgreen") +
  facet_grid(Feedback~Period) +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  theme_minimal()
