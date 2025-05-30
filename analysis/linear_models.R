pacman::p_load(tidyverse, lme4, broom, performance, patchwork, here, modelr)

data <- read_csv(here("data", "Df.csv")) %>%
  filter(!(Subjs %in% c(2, 20, 26)))

data %>% ggplot(aes(x = Peak_interval, y = Asyns_c)) +
  geom_point(aes(color = Effector), alpha = .2) +
  geom_smooth(method = "lm", se = FALSE, color = "black") +
  geom_abline(intercept = 0, slope = 0, linetype = "dashed") +
  facet_wrap(.~Period) +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  theme_minimal()

model <- lmer(data = data,
              Asyns_c ~ Peak_interval + Period + (1|Subjs/Trial) +
                offset(-Peak_interval))
summary(model)
parameters::model_parameters(model)

data_summ <- data %>%
  group_by(Subjs, Period, Cond, Trial, Effector) %>%
  summarise(m_Asyn_c = mean(Asyns_c),
            m_Peak_interval = mean(Peak_interval)) %>%
  mutate(ISI = factor(Period)) %>%
  filter(m_Asyn_c < 50)

model_summ <- lmer(data = data_summ,
                   m_Asyn_c ~ m_Peak_interval * ISI + (1|Subjs) -
                     offset(-m_Peak_interval))
summary(model_summ)
parameters::model_parameters(model_summ)
performance::check_model(model_summ)

data_summ <- data_summ %>%
  add_predictions(model_summ)

data_summ %>% ggplot(aes(x = m_Peak_interval, y = m_Asyn_c)) +
  geom_point(aes(color = Effector), alpha = .2) +
  geom_smooth(method = "lm", se = FALSE, color = "black") +
  geom_abline(intercept = 0, slope = 0, linetype = "dashed") +
  facet_wrap(.~Period) +
  scale_color_manual(values = c("#0072B2", "#D55E00")) +
  theme_minimal()

