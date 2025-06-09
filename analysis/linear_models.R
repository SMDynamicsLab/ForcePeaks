pacman::p_load(tidyverse, lme4, broom, modelsummary, patchwork, here, modelr, wesanderson)

# Acá están los datos de todas las versiones del experimento
data <- read_csv(here("data", "Df_2025.csv")) %>%
  filter(!(Subjs %in% c(2, 20, 26))) %>%
  select(- `...1`) %>%
  mutate(Effector = if_else(Effector == "D", "Finger", "Wrist"),
         Period = paste(Period, "ms"),
         Feedback = if_else(Subjs <= 26, "Feedback", "No Feedback")) # Entiendo que los tomados por Ariel no tienen Feedback

datasummary_skim(data)

# Lo primero que tenemos que hacer es mostrar que hay una diferencia sistemática entre los picos 
# para ambos efectores, y que esta diferencia es consistente a lo largo de los periodos.
data %>% ggplot(aes(x = Effector, 
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

# Ahora veamos que pinta tiene esto.
data %>% ggplot(aes(x = Peak_interval, y = Asyns_c)) +
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
model <- lmer(data = data %>%
                filter(Asyns_c < 100),
              Asyns_c ~ Peak_interval * Period * Feedback + (1|Subjs/Trial) +
                offset(-Peak_interval))
performance::check_model(model)

# Ahora hagamos los promeido por trial y de nuevo saquemos asincronías mayores a +50ms
data_summ <- data %>%
  group_by(Subjs, Period, Cond, Trial, Effector, Feedback) %>%
  summarise(m_Asyn_c = mean(Asyns_c),
            Peak_interval = mean(Peak_interval)) %>%
  filter(m_Asyn_c < 50)

model_summ <- lmer(data = data_summ,
                   m_Asyn_c ~ Peak_interval * Period * Feedback + (1|Subjs) +
                     offset(-Peak_interval))
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
                   m_Asyn_c ~ Peak_interval * Period + (1|Subjs) +
                     offset(-Peak_interval))

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
                          m_Asyn_c ~ Peak_interval * Period + (1|Subjs) +
                            offset(-Peak_interval))

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

