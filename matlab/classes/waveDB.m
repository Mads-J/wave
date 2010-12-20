classdef waveDB
    %WAVEDB Database layer specifically for interacting with the wave
    %database
    %
    %   Detailed explanation goes here
    
    properties
        con;        % database connection handle
        vectorSelectTemplate = ['SELECT  ',...
            '  ###PREFIX###datetime,         ',...
            '  ###PREFIX###speed,            ',...
            '  ###PREFIX###direction,        ',...
            '  ST_X(###PREFIX###location),   ',...
            '  ST_Y(###PREFIX###location),   ',...
            '  tblsource.srcname,           ',...
            '  tblsource.srcconfig,         ',...
            '  tblsource.srcbeginexecution, ',...
            '  tblsource.srcendexecution,   ',...
            '  tblsource.srcsourcetypeid    ',...
            ' FROM                          ',...
            '  ###TABLE###,                 ',...
            '  public.tblsource             ',...
            ' WHERE                         ',...
            '  ###PREFIX###sourceid = tblsource.srcid'];
    end
    
    methods
        function db = waveDB(dbconfig)
            db.con = database(dbconfig.database,dbconfig.username,...
                dbconfig.password,dbconfig.jdbcDriver,dbconfig.driverURL);
            setdbprefs('DataReturnFormat','structure');
        end
        function dField = selectWind(db,source,tBegin,tEnd,location)
            if(nargin<2)
                error(['Must provide a source name, use wavedb.showSources'...
                    ' to see a list of the possible source names']);
            end
            sql = [regexprep(db.vectorSelectTemplate,...
            regexprep(db.vectorSelectTemplate,'###PREFIX###','tblwind.win'),...
            '###TABLE###','public.tablewind'),...
                ' AND tblsource.srcname = ''',source,''''];
            
            if(nargin>2)
                sql = [sql,' AND tblwind.windatetime >= ''',...
                    datestr(tBegin,'yyyy-mm-dd HH:MM:SS'),''''];
            end
            if(nargin>3)
                sql = [sql,' AND tblwind.windatetime <= ''',...
                    datestr(tEnd,'yyyy-mm-dd HH:MM:SS'),''''];
            end
            
            raw = fetch(db.con,sql);
            if(size(raw,1)==0)
                error('Empty result set found')
            end
            n = size(raw.st_x,1);
            win(n) = wind;
            for i=1:n
                win(i) = wind(raw.srcname(i),...
                    raw.windatetime(i),...
                    [raw.st_x(i),raw.st_y(i)],...
                    raw.winspeed(i),...
                    raw.windirection(i),...
                    'm/s',...
                    'deg');
            end
            dField = dataField(win);
        end
        
        function dField = selectCurrent(db,source,tBegin,tEnd,location)
            if(nargin<2)
                error(['Must provide a source name, use wavedb.showSources'...
                    ' to see a list of the possible source names']);
            end
            sql = [regexprep(...
            regexprep(db.vectorSelectTemplate,'###PREFIX###','tblcurrent.cur'),...
            '###TABLE###','public.tblcurrent'),...
                ' AND tblsource.srcname = ''',source,''''];
            
            if(nargin>2)
                sql = [sql,' AND tblcurrent.curdatetime >= ''',...
                    datestr(tBegin,'yyyy-mm-dd HH:MM:SS'),''''];
            end
            if(nargin>3)
                sql = [sql,' AND tblcurrent.curdatetime <= ''',...
                    datestr(tEnd,'yyyy-mm-dd HH:MM:SS'),''''];
            end
            
            raw = fetch(db.con,sql);
            if(size(raw,1)==0)
                error('Empty result set found')
            end
            n = size(raw.st_x,1);
            cur(n) = current;
            for i=1:n
                cur(i) = current(raw.srcname(i),...
                    raw.curdatetime(i),...
                    [raw.st_x(i),raw.st_y(i)],...
                    raw.curspeed(i),...
                    raw.curdirection(i),...
                    'm/s',...
                    'deg');
            end
            dField = dataField(cur,{'speed','dir'});
        end
        
        function dField = selectSpectra(db,source,tBegin,tEnd,location)
            if(nargin<2)
                error(['Must provide a source name, use wavedb.showSources'...
                    ' to see a list of the possible source names']);
            end
            sql = ['SELECT  ',...
                '  tblwave.wavdatetime,         ',...
                '  tblwave.wavspectra,          ',...
                '  tblwave.wavheight,           ',...
                '  tblwave.wavpeakdir,          ',...
                '  tblwave.wavpeakperiod,       ',...
                '  ST_X(tblwave.wavlocation),   ',...
                '  ST_Y(tblwave.wavlocation),   ',...
                '  tblspectrabin.spcfreq,       ',...
                '  tblspectrabin.spcdir,        ',...
                '  tblsource.srcname,           ',...
                '  tblsource.srcconfig,         ',...
                '  tblsource.srcbeginexecution, ',...
                '  tblsource.srcendexecution,   ',...
                '  tblsource.srcsourcetypeid    ',...
                ' FROM                          ',...
                '  public.tblwave,              ',...
                '  public.tblspectrabin,        ',...
                '  public.tblsource             ',...
                ' WHERE                         ',...
                '  tblwave.wavspectrabinid = tblspectrabin.spcid AND ',...
                '  tblwave.wavsourceid = tblsource.srcid',...
                ' AND tblsource.srcname = ''',source,''''];
            
            if(nargin>2)
                sql = [sql,' AND tblwave.wavdatetime >= ''',...
                    datestr(tBegin,'yyyy-mm-dd HH:MM:SS'),''''];
            end
            if(nargin>3)
                sql = [sql,' AND tblwave.wavdatetime <= ''',...
                    datestr(tEnd,'yyyy-mm-dd HH:MM:SS'),''''];
            end
            
            rawspec = fetch(db.con,sql);
            if(size(rawspec,1)==0)
                error(['Empty result set found with query: ',sql]);
            end
            n = size(rawspec.st_x,1);
            spec(n) = spectra;
            for i=1:n
                spec(i) = spectra(rawspec.srcname(i),...
                    rawspec.wavdatetime(i),...
                    [rawspec.st_x(i),rawspec.st_y(i)],...
                    double(rawspec.wavspectra{i}.getArray()),...
                    double(rawspec.spcfreq{i}.getArray()),...
                    double(rawspec.spcdir{i}.getArray()));
            end
            dField = dataField(spec,{'hs','tp','te'});
        end
        function names = showSources(db)
            sql = ['SELECT  ',...
                '  DISTINCT ON(src.srcid)   ',...
                '  src.srcid,               ',...
                '  src.srcname,             ',...
                '  sty.sourcetypename      ',...
                'FROM                       ',...
                '  public.tblsource src     ',...
                'LEFT JOIN                  ',...
                '  public.tblwave wav    ON src.srcid=wav.wavsourceid ',...
                'LEFT JOIN                  ',...
                '  public.tblwind win    ON src.srcid=win.winsourceid ',...
                'LEFT JOIN                  ',...
                '  public.tblcurrent cur ON src.srcid=cur.cursourceid ',...
                'LEFT JOIN                  ',...
                '  public.tblbathy bat   ON src.srcid=bat.batsourceid ',...
                'LEFT JOIN                  ',...
                '  public.tblsourcetype sty ON src.srcsourcetypeid=sty.sourcetypeid ',...
                'ORDER BY src.srcid, sty.sourcetypename'
                ];
            rawnames = fetch(db.con,sql);
            
            m = size(rawnames.srcid,1);
            dat = cell(m,6);
            for i=1:m
                sql = ['SELECT  ',...
                    '  MIN(wav.wavdatetime) dwavmin,               ',...
                    '  MAX(wav.wavdatetime) dwavmax,               ',...
                    '  MIN(ST_X(wav.wavlocation)) xwavmin,               ',...
                    '  MAX(ST_X(wav.wavlocation)) xwavmax,               ',...
                    '  MIN(ST_Y(wav.wavlocation)) ywavmin,               ',...
                    '  MAX(ST_Y(wav.wavlocation)) ywavmax,               ',...
                    '  MIN(win.windatetime) dwinmin,               ',...
                    '  MAX(win.windatetime) dwinmax,               ',...
                    '  MIN(ST_X(win.winlocation)) xwinmin,               ',...
                    '  MAX(ST_X(win.winlocation)) xwinmax,               ',...
                    '  MIN(ST_Y(win.winlocation)) ywinmin,               ',...
                    '  MAX(ST_Y(win.winlocation)) ywinmax,               ',...
                    '  MIN(cur.curdatetime) dcurmin,               ',...
                    '  MAX(cur.curdatetime) dcurmax,              ',...
                    '  MIN(ST_X(cur.curlocation)) xcurmin,               ',...
                    '  MAX(ST_X(cur.curlocation)) xcurmax,               ',...
                    '  MIN(ST_Y(cur.curlocation)) ycurmin,               ',...
                    '  MAX(ST_Y(cur.curlocation)) ycurmax,               ',...
                    '  MIN(ST_X(bat.batlocation)) xbatmin,               ',...
                    '  MAX(ST_X(bat.batlocation)) xbatmax,               ',...
                    '  MIN(ST_Y(bat.batlocation)) ybatmin,               ',...
                    '  MAX(ST_Y(bat.batlocation)) ybatmax               ',...
                    'FROM                       ',...
                    '  public.tblsource src     ',...
                    'LEFT JOIN                  ',...
                    '  public.tblwave wav    ON src.srcid=wav.wavsourceid ',...
                    'LEFT JOIN                  ',...
                    '  public.tblwind win    ON src.srcid=win.winsourceid ',...
                    'LEFT JOIN                  ',...
                    '  public.tblcurrent cur ON src.srcid=cur.cursourceid ',...
                    'LEFT JOIN                  ',...
                    '  public.tblbathy bat   ON src.srcid=bat.batsourceid ',...
                    'LEFT JOIN                  ',...
                    '  public.tblsourcetype sty ON src.srcsourcetypeid=sty.sourcetypeid ',...
                    'WHERE src.srcid=''',...
                    char(rawnames.srcid(i)),''''];
                rawextents = fetch(db.con,sql);
                
                dat(i,1:2) = {char(rawnames.srcname(i)),...
                    char(rawnames.sourcetypename(i))};
                if(strcmp(rawextents.dwavmin,'null'))
                    dat(i,3) = {'NA'};
                else
                    dat(i,3) = {['TB:',char(rawextents.dwavmin),...
                        ',TE:',char(rawextents.dwavmax),...
                        ',LL:',num2str(rawextents.ywavmin),...
                        ',',num2str(rawextents.xwavmin),...
                        ',UR:',num2str(rawextents.ywavmax),...
                        ',',num2str(rawextents.xwavmax)]};
                end
                if(strcmp(rawextents.dwinmin,'null'))
                    dat(i,4) = {'NA'};
                else
                    dat(i,4) = {['TB:',char(rawextents.dwinmin),...
                        ',TE:',char(rawextents.dwinmax),...
                        ',LL:',num2str(rawextents.ywinmin),...
                        ',',num2str(rawextents.xwinmin),...
                        ',UR:',num2str(rawextents.ywinmax),...
                        ',',num2str(rawextents.xwinmax)]};
                end
                if(strcmp(rawextents.dcurmin,'null'))
                    dat(i,5) = {'NA'}
                else
                    dat(i,5) = {['TB:',char(rawextents.dcurmin),...
                        ',TE:',char(rawextents.dcurmax),...
                        ',LL:',num2str(rawextents.ycurmin),...
                        ',',num2str(rawextents.xcurmin),...
                        ',UR:',num2str(rawextents.ycurmax),...
                        ',',num2str(rawextents.xcurmax)]};
                end
                if(isnan(rawextents.xbatmin))
                    dat(i,6) = {'NA'};
                else
                    dat(i,6) = {['LL:',num2str(rawextents.ybatmin),...
                        ',',num2str(rawextents.xbatmin),...
                        ',UR:',num2str(rawextents.ybatmax),...
                        ',',num2str(rawextents.xbatmax)]};
                end
            end
            vertPerRecord =  20;
            f = figure('Position',[200 200 1000 130+m*vertPerRecord]);
            cnames = {'Source Name','Source Type','Wave Spectra','Wind','Current','Bathymetry'};
            columnformat = {'char', 'char', 'logical','logical','logical','logical'};
            t = uitable('Parent',f,'Data',dat,'ColumnName',cnames,...
                'Position',[20 20 960 80+m*vertPerRecord]);
            set(t,'ColumnWidth',{170,170,125,125,125,125})
        end
    end
end