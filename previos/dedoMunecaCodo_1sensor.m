clear;

%Tapping con 3 efectores: dedo, muneca, codo. Un bloque para cada efector.
%Series isócronas de 30 bips.
%ISIs=[400 650];
%3 bloques, un efector en cada bloque
%12 trials de cada ISI y cada efector, total: 72 trials. 
%ISIs randomizados dentro de cada bloque
%NStim siempre 30, el arduino registra la fuerza de los últimos 25 taps
%Los 5 primeros bips serán recortados
%Éste código fue escrito sobre un código anterior largamente probado. Para no alterar 
%la lógica del código y así aumentar la probabilidad de que falle, se
%utilizará un valor fijo de perturb_bip=15, y otro de perturb_size=0. No cambiar el valor 
%de perturb_bip=15 porque el arduino lo usa como referencia para definir los taps en los que 
%registra la fuerza.
%Se puede ussar sin feedback (tapping_mode=1) o con feedback (tapping_mode=2)

%Al finalizar cada bloque, guarda 5 archivos correspondientes a 
%ese bloque: stims, resps, asyns, voltaje, params

% Va con dedoMunecaCodo_1sensor.ino

%%
%Habilitación de Plots
%plotOn true: grafica los trials que salen bien
%plotOn false: no grafica nada
plotOn=false;

%%
% set principal parameters

N_trials_per_cond = 2;	 % number of trials per ISI per efector 
N_blocks = 2; %3 bloques de 24 trials cada uno (puede haber un descancito a los 10)

efector=shuffle(1:2); %1 dedo, 2 muñeca, 3 codo
ISIs=[400 650]; % interstimulus interval (milliseconds)
tapping_mode=2; %1 sin feedback, 2 con feedback
% N_stim = 23; %así anda, el Arduino registra la fuerza de 16 taps
N_stim = 30; %el Arduino registra la fuerza de 25 taps

event_type = 2;
sensorThreshold = 50;     % pressure sensor threshold (0 to 1024) (por ahora no est� en uso)
perturb_bip = 15; %valor fijo, ver expliacación arriba en este script y en script de arduino
perturb_size=0; %series isócronas

%other parameters
N_trials_per_block = length(ISIs)*N_trials_per_cond;
% trials_fallidos=zeros(4,2);
error_flag=false;
plot_flag=0;
descancito_flag=0;
BIEN_counter=0;

%%
%Subject initials

subject = input('Tipee sus 3 iniciales (nombre, 2do nombre, apellido): ','s');
disp(' ');

%% start communication with Arduino

%ardu = serial('COM4'); %Windows
% ardu = serial('/dev/tty.usbserial-A9007Qr6'); %MAC
%ardu = serial('/dev/ttyUSB0');                  % UBUNTU
%ardu = serial('/dev/ttyACM0');
ardu = serial('/dev/ttyACM0','BaudRate',115200);
% ardu = serial('/dev/ttyS0','BaudRate',115200);

fopen(ardu);
ardu_timeout = 30;
set(ardu,'Timeout',ardu_timeout);
pause(2);		% wait for fopen to complete

if ardu_timeout*1000 < perturb_bip*500 + (N_stim-perturb_bip)*(500)%
    disp('Error: serial port timeout too short.');
    fclose(ardu);
    return;
end


%% main loop

% loop through all blocks
for block = 1:N_blocks
    descancito_flag=0;
    
    if efector(block)==1     %dedo
        efectorActual='DEDO';
        texto='el dedo';
    elseif efector(block)==2 %muñeca
        efectorActual='MUNE';
        texto='la muñeca';
    else                     %codo    
        efectorActual='CODO';
        texto='el codo';
    end
    
    disp(' ')
    
    if block > 1
        disp(' ');
        disp(['XXXXXX FIN DE BLOQUE ' num2str(block-1) ' XXXXXX']);
        disp('Tome un descanso antes del siguiente bloque.');
        go = input('Presione la tecla "return" cuando esté listo para comenzar.','s');
        disp(' ');
        
        % opciones ocultas: q+return to quit.
        if strcmp(go,'q')
            fclose(ardu);
            return;
        end
    end
           
    fecha = datestr(fix(clock),'yyyy-mm-dd-HH-MM');
    savefile_stims = [subject '-' fecha '-' efectorActual    '-stims.mat'];
    savefile_resps = [subject '-' fecha '-' efectorActual    '-resps.mat'];
    savefile_asyns = [subject '-' fecha '-' efectorActual    '-asyns.mat'];
    savefile_params = [subject '-' fecha '-' efectorActual   '-params.mat'];
    savefile_voltajes = [subject '-' fecha '-' efectorActual '-voltajes.mat'];
    
    stims  = [];
    resps  = [];
    respsI  = [];
    %respsD  = [];
    asyns = [];
    debrief_perce = [];
    debrief_intro = [];
    voltajes=[];
    
    ISIPerBlock=shuffle(repmat(ISIs',N_trials_per_cond,1));
    ISI=ISIPerBlock;
    
    
    % loop through all trials
    i = 1;
    N_trials_per_block_actual = N_trials_per_block;
    
    while i <= N_trials_per_block_actual
                        
        % send parameters
        message = sprintf('ARDU;I%d;N%d;P%d;B%d;E%d;M%d;T%d;X',[ISI(i) N_stim perturb_size perturb_bip event_type tapping_mode sensorThreshold]);
        if i==1
            disp(message)
            pause
            clc
        end
        
        fprintf(ardu,message);
        
        disp([num2str(i) '/' num2str(N_trials_per_block_actual) ]);
        
        % disp(['Trials fallidos: '  num2str(trials_fallidos_mas50+trials_fallidos_menos50)]);
        % disp(['Condición número: ' num2str(tapping_mode_actual) ]);
                
        disp(['Tapee con ' texto ' en el sensor. "Enter" para comenzar.']);
                
        fprintf('\n')
        go=input('','s');
        
        % opciones ocultas: q+return to quit, sq+return to save block and skip to next block.
        if strcmp(go,'q')
            fclose(ardu);
            return;
        end
        
        pause(1.5*rand(1) + 0.5);
        
        % start trial
        message = sprintf('ARDU;');
        fprintf(ardu,message);
                
        %read trial data from arduino
        d1 = [];
        aux = fgetl(ardu);
        counter=1;
        while (~strcmp(aux(1),'E'))
            d1{counter} = aux;
            aux = fgetl(ardu);
            counter=counter+1;
        end
        
        %read voltaje del sensor from Arduino
        d2 = [];
        voltaje=[];
        aux = fgetl(ardu);
        counter=1;
        while (~strcmp(aux(1),'F'))
            d2{counter} = aux;
            aux = fgetl(ardu);
            counter=counter+1;
        end
        
        %Manipulación - Valores de voltaje del sensor
        n2 = length(d2);
        for ii=1:n2
            temp=d2{ii};
            ind1=find(temp==':')-1;
            voltaje(ii)=str2num(temp(1:ind1));
        end
        
        
        
        if length(voltaje)>5000 %%podría llegar a pasar si el sujeto mete muchos taps
            voltaje=[];
        end
        
        voltaje(length(voltaje)+1:5000)=0; %completa con  ceros al final para que todos tengan la misma longitud
        
        % separate stimuli and responses
        nn = length(d1);			% number of stimuli + responses
        temp1 = zeros(nn,1);
        temp1_I = zeros(nn,1); %respuestas provenientes del sensor de la izquierda
        %temp1_D = zeros(nn,1); %respuestas provenientes del sensor de la derecha o Lanata
        temp2 = zeros(nn,1);
        temp3 = zeros(nn,1);
        
        for ii = 1:nn
            % 1: si es estimulo, 0: si es respuesta
            temp1(ii) = sum(ismember(d1{ii},'S'));
            temp1_I(ii) = sum(ismember(d1{ii},'I')); %%respuestas en el sensor de la izquierda
            %temp1_D(ii) = sum(ismember(d1{ii},'D')); %%respuestas en el sensor de la derecha o Leuco
            
            % el numero de estimulo/respuesta
            if ismember(d1{ii}(4),':');
                temp2(ii)  = str2num(d1{ii}(3));
            elseif ismember(d1{ii}(5),':');
                temp2(ii) = str2num(d1{ii}(3:4));
            end
            
            % el tiempo
            l1 = d1{ii};
            ind1 = find(l1==':')+2;
            ind2 = find(l1==';')-1;
            temp3(ii) = str2num(l1(ind1:ind2));
        end
        
        stim  = [repmat(i,sum(temp1),1) temp2(temp1==1) temp3(temp1==1)];
        resp  = [repmat(i,sum(~temp1),1) temp2(~temp1) temp3(~temp1)];
        respI  = [repmat(i,sum(temp1_I),1) temp2(~~temp1_I) temp3(~~temp1_I)];
        %respD  = [repmat(i,sum(temp1_D),1) temp2(~~temp1_D) temp3(~~temp1_D)];
        
        
        % Compute asynchronies
        if isempty(resp)
            first_stim_responded = N_stim;
            last_valid_resp =  N_stim;
        else
            first_stim_responded = find((abs(stim(:,3) - resp(1,3)) < ISI(i)/2));
            last_valid_resp =  find((abs(stim(end,3) - resp(:,3)) < ISI(i)/2));
        end
        
        %%Posibles errores
        %Condiciones para aceptar un trial como correcto.
        %1) Cantidad de respuestas igual a cantidad de est�mulos a partir del primero respondido.
        %2) No puede dejar pasar más de 3 bips antes de empezar.
        %3) En tapping mode 3 y 4 el cambio de sensor se tiene que dar en la perturbación
        %4) Que no haya asincronías mayores a 250 ms
        
%         if isempty(respD)==1
%             respD=[repmat(i,10,1) repmat(0,10,1) repmat(0,10,1)];
%         end
        if isempty(respI)==1
            respI=[repmat(i,10,1) repmat(0,10,1) repmat(0,10,1)];
        end
        
        if (length(1:last_valid_resp) < length(first_stim_responded:N_stim))
            disp(['Warning: faltó una respuesta']);
            asyn_values = nan(length(first_stim_responded:N_stim),1);
            asyn = [repmat(i,N_stim-first_stim_responded+1,1) [first_stim_responded:N_stim]' [first_stim_responded:N_stim]'-perturb_bip asyn_values];
            plot_flag = 0;
            error_flag=true;
        elseif (length(1:last_valid_resp) > length(first_stim_responded:N_stim))
            disp(['Warning: hubo una respuesta de más.']);
            asyn_values = nan(length(first_stim_responded:N_stim),1);
            asyn = [repmat(i,N_stim-first_stim_responded+1,1) [first_stim_responded:N_stim]' [first_stim_responded:N_stim]'-perturb_bip asyn_values];
            plot_flag = 0;
            error_flag=true;
            
        elseif (first_stim_responded>4)
            disp(['Warning: no dejar pasar más de 4 bips sin empezar a tapear.']);
            asyn_values = nan(length(first_stim_responded:N_stim),1);
            asyn = [repmat(i,N_stim-first_stim_responded+1,1) [first_stim_responded:N_stim]' [first_stim_responded:N_stim]'-perturb_bip asyn_values];
            plot_flag = 0;
            error_flag=true;
%         elseif ((tapping_mode_actual==3 || tapping_mode_actual==4 ) && length(stim)-last_valid_resp+respD(1,2)~=perturb_bip+1)
%             if length(stim)-last_valid_resp+respD(1,2)>perturb_bip+1
%                 disp('Warning: el cambio de sensor ocurrió después que el cambio de tempo.');
%             else
%                 disp('Warning: el cambio de sensor ocurrió antes que el cambio de tempo.');
%             end
%             asyn_values = nan(length(first_stim_responded:N_stim),1);
%             asyn = [repmat(i,N_stim-first_stim_responded+1,1) [first_stim_responded:N_stim]' [first_stim_responded:N_stim]'-perturb_bip asyn_values];
%             plot_flag = 0;
%             error_flag=true;
        else
            asyn_values = resp(1:last_valid_resp,3)-stim(first_stim_responded:end,3);
            if any(find(abs(asyn_values)>(ISI(i)/2)))==1 %si la asincron�a de alguna respuesta es mayor que 200 ms anula el trial
                disp(['Warning: Asincronía mayor que 300 ms.']);
                asyn_values = nan(length(first_stim_responded:N_stim),1);
                asyn = [repmat(i,N_stim-first_stim_responded+1,1) [first_stim_responded:N_stim]' [first_stim_responded:N_stim]'-perturb_bip asyn_values];
                plot_flag = 0;
                error_flag=true;
            else
                % format: trial_number , stim_number , stim_number_relative_to_perturb , asyn
                %Festejo y descansito
                disp(['BIEN' repmat('!',1,floor(10*rand(1)) + 1)]);
                
                asyn = [repmat(i,N_stim-first_stim_responded+1,1) [first_stim_responded:N_stim]' [first_stim_responded:N_stim]'-perturb_bip asyn_values];
                plot_flag=0;
                if plotOn==true %habilita el plot
                    plot_flag = 1;
                end
                error_flag=false;
                %Descansito (1:30) en la mitad del bloque
                %Se da cuando la mitad de los trials del bloque están bien hechos
                BIEN_counter=BIEN_counter+1;
                
                if (BIEN_counter==round((length(ISIs)*N_trials_per_cond/2)) && descancito_flag==0)
                    disp('');
                    disp('Descansito a mitad del bloque. Presione enter para seguir.')
                    disp('');
                    pause;
                    descancito_flag=1;
                   
                end
                
                
            end
        end
        
        fprintf('\n')
%         %Trials fallidos según signo de la perturbación
%         if error_flag==true;
%             if perturb_size(i)>0;
%                 trials_fallidos_slowDownPert=trials_fallidos_slowDownPert+1;
%             elseif perturb_size(i)<0;
%                 trials_fallidos_speedUpPert=trials_fallidos_speedUpPert+1;
%             end
%             
%         end
        
        asyns = [asyns; asyn];
        stims = [stims; stim];
        resps = [resps; resp];
        respsI = [respsI; respI];
        %respsD = [respsD; respD];
        voltajes=[voltajes; voltaje];
        
        
        % plot
        if plot_flag == 1
            figure(1);
            clf(1);
            subplot(2,1,1);
            plot(resp(:,3),ones(length(resp),1),'b+','markersize',20);
            hold on;
            line([stim(perturb_bip,3) stim(perturb_bip,3)],[-1 2]);
            plot(stim(:,3),zeros(N_stim,1),'r+','markersize',20);
            axis([stim(1,3)-ISI(i) resp(end,3)+ISI(i) -1 2]);
            set(gca,'YTick',-1:1:2)
            set(gca,'YTickLabel',{'','stim','resp',''});
            xlabel('absolute time');
            legend('last trial');
            subplot(2,1,2);
            plot(stim(first_stim_responded:end,3),asyn(:,4),'b.-');
            hold on;
            line([stim(perturb_bip,3) stim(perturb_bip,3)],[-200 200]);
            axis([stim(1,3)-ISI(i) resp(end,3)+ISI(i) -200 200]);
            % set(gca,'XTickLabel',{''});
            xlabel('absolute time');
            ylabel('asyn (ms)');
            
            figure(2);
            if (perturb_size > 0)
                plot(asyn(:,3),asyn(:,4),'b.-');
            else
                plot(asyn(:,3),asyn(:,4),'g.-');
            end
            hold on;
            line([0 0],[-200 200]);
            xlabel('stim number');
            ylabel('asyn (ms)');
            legend('all trials');
        end
        
        %Plot voltaje
        if plot_flag==1
            figure(3)
            ind=find(voltaje==2000); %identifica los comienzos de taps
            voltaje_para_plot=voltaje;
            voltaje_para_plot(ind)=0;
            plot(voltaje_para_plot)
        end
        
        
        % start new trial; if missing/extra responses, repeat trial at the end of the block
        if isnan(asyn_values(1))
            ISI = [ISI; ISI(i)];
            ISI(i)=nan;
            N_trials_per_block_actual = N_trials_per_block_actual + 1;
            
        end
        
        
        % debriefing for all tapping modes
        %debrief_perce_single = 'X';
        
        
        %    while strcmp(debrief_perce_single,'S') == 0 && strcmp(debrief_perce_single,'N') == 0
        %        debrief_perce_single = upper(input('�Percibi� alguna alteraci�n en la secuencia? (S/N)','s'));
        %    end
        %    if strcmp(debrief_perce_single,'S') == 1
        %        while strcmp(debrief_perce_single,'R') == 0 && strcmp(debrief_perce_single,'A') == 0
        %			debrief_perce_single = upper(input('�Lo que percibi� fue un Retraso o un Adelanto? (R/A)','s'));
        %        end
        %  end
        %debrief_intro_single = 0;
        
        %	while debrief_intro_single == 0
        %		debrief_intro_single = input('En una escala de 1 a 10, �cu�l cree que fue su desempe�o? (1=muy mal / 10=muy bien)','s');
        %	end
        
        %disp(' ');
        
        %debrief_perce = [debrief_perce; debrief_perce_single];
        %debrief_intro = [debrief_intro; debrief_intro_single];
        %         if error_flag==false
        %             input('Ingrese la cantidad de unos (1/2/3): ','s');
        %             fprintf('\n')
        %         end
        
        i = i + 1;
        
    end
%     trials_fallidos(tapping_mode_actual,1)=trials_fallidos_slowDownPert;
%     trials_fallidos(tapping_mode_actual,2)=trials_fallidos_speedUpPert;
%     
    
    
    % save block data
    save(['/home/leo/Dropbox/Doctorado/experimentos/2018/dedoMunecaCodo/sujetos/' savefile_stims],'stims');
%     save(['/home/leo/Dropbox/Doctorado/experimentos/2018/dedoMunecaCodo/sujetos/' savefile_resps],'resps','respsI','respsD');
    save(['/home/leo/Dropbox/Doctorado/experimentos/2018/dedoMunecaCodo/sujetos/' savefile_resps],'resps','respsI');
    save(['/home/leo/Dropbox/Doctorado/experimentos/2018/dedoMunecaCodo/sujetos/' savefile_asyns],'asyns');
    save(['/home/leo/Dropbox/Doctorado/experimentos/2018/dedoMunecaCodo/sujetos/' savefile_params],'N_trials_per_block','N_trials_per_block_actual','ISIs','ISI','ISIPerBlock','N_stim','tapping_mode','event_type','perturb_bip','perturb_size','debrief_perce','debrief_intro','efector','efectorActual');
    save(['/home/leo/Dropbox/Doctorado/experimentos/2018/dedoMunecaCodo/sujetos/' savefile_voltajes],'voltajes');
    
%     trials_fallidos_slowDownPert=0;
%     trials_fallidos_speedUpPert=0;
%     trials_fallidos=zeros(4,2);
    BIEN_counter=0;
end
disp(' ')
disp('Fin del experimento')

fclose(ardu);




