

import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';

const COLORS = ['#000080', '#1084d0', '#4040a0'];
const SOURCE_COLORS = {
  News: '#000080',
  Pricing: '#1084d0',
  GitHub: '#4040a0'
};

function MentionsChart({ stats }) {
  const data = stats.map(s => ({
    name: s.competitor.charAt(0).toUpperCase() + s.competitor.slice(1),
    mentions: s.news_count
  }));

  return (
    <div className="inset-box" style={{ marginBottom: 8 }}>
      <div className="section-label" style={{ marginBottom: 8 }}>
        WEEKLY MENTIONS
      </div>
      <ResponsiveContainer width="100%" height={120}>
        <BarChart data={data} barSize={30}>
          <XAxis
            dataKey="name"
            tick={{ fontFamily: 'VT323', fontSize: 14, fill: '#000080' }}
            axisLine={false}
            tickLine={false}
          />
          <YAxis
            tick={{ fontFamily: 'VT323', fontSize: 13, fill: '#000080' }}
            axisLine={false}
            tickLine={false}
            width={20}
          />
          <Tooltip
            contentStyle={{
              fontFamily: 'VT323',
              fontSize: 14,
              background: '#c0c0c0',
              border: '2px solid #808080',
              borderRadius: 0
            }}
          />
          <Bar dataKey="mentions" radius={0}>
            {data.map((_, i) => (
              <Cell key={i} fill={COLORS[i % COLORS.length]} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

function SourceDonut({ competitor, news, pricing, github }) {
  const data = [
    { name: 'News', value: news },
    { name: 'Pricing', value: pricing },
    { name: 'GitHub', value: github },
  ].filter(d => d.value > 0);

  if (data.length === 0) return null;

  if (data.length === 1) {
    return (
      <div style={{ textAlign: 'center' }}>
        <div style={{ fontSize: 13, color: '#000080', marginBottom: 4 }}>
          {competitor.toUpperCase()}
        </div>
        <div style={{
          width: 88,
          height: 88,
          borderRadius: '50%',
          background: SOURCE_COLORS[data[0].name],
          margin: '0 auto',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          color: '#fff',
          fontSize: 13,
          fontFamily: 'VT323'
        }}>
          {data[0].value} {data[0].name}
        </div>
      </div>
    );
  }

  return (
    <div style={{ textAlign: 'center' }}>
      <div style={{ fontSize: 13, color: '#000080', marginBottom: 4 }}>
        {competitor.toUpperCase()}
      </div>
      <PieChart width={140} height={100}>
        <Pie
          data={data}
          cx={70}
          cy={50}
          innerRadius={28}
          outerRadius={44}
          dataKey="value"
          strokeWidth={0}
        >
          {data.map((entry, i) => (
            <Cell key={i} fill={SOURCE_COLORS[entry.name]} />
          ))}
        </Pie>
        <Tooltip
          contentStyle={{
            fontFamily: 'VT323',
            fontSize: 13,
            background: '#c0c0c0',
            border: '2px solid #808080',
            borderRadius: 0
          }}
        />
      </PieChart>
    </div>
  );
}

export default function StatsPanel({ stats }) {
  if (!stats || stats.length === 0) return null;

  const mostActive = stats.reduce((a, b) =>
    a.news_count > b.news_count ? a : b
  );

  return (
    <div style={{ marginBottom: 12 }}>
      <div className="inset-box" style={{ marginBottom: 8 }}>
        <div className="section-label" style={{ marginBottom: 6 }}>
          WEEKLY PULSE
        </div>
        <div style={{ display: 'flex', gap: 24, fontSize: 14, color: '#000' }}>
          <span>
            🔴 Most active:{' '}
            <strong style={{ color: '#000080' }}>
              {mostActive.competitor.toUpperCase()}
            </strong>{' '}
            ({mostActive.news_count} mentions)
          </span>
          <span>
            🟡 Quietest:{' '}
            <strong style={{ color: '#000080' }}>
              {stats.reduce((a, b) =>
                a.news_count < b.news_count ? a : b
              ).competitor.toUpperCase()}
            </strong>
          </span>
        </div>
      </div>

      <MentionsChart stats={stats} />

      <div className="inset-box">
        <div className="section-label" style={{ marginBottom: 8 }}>
          SOURCE BREAKDOWN
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-around' }}>
          {stats.map(s => (
            <SourceDonut
              key={s.competitor}
              competitor={s.competitor}
              news={s.news_count}
              pricing={s.pricing_count}
              github={s.github_count}
            />
          ))}
        </div>
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          gap: 16,
          fontSize: 13,
          marginTop: 4
        }}>
          {Object.entries(SOURCE_COLORS).map(([name, color]) => (
            <span key={name} style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
              <span style={{
                width: 10,
                height: 10,
                background: color,
                display: 'inline-block',
                border: '1px solid #808080'
              }} />
              {name}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}