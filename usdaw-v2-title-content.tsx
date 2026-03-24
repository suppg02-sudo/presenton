const layoutId = "title-and-content";
const layoutName = "Title and Content";
const layoutDescription = "Standard content slide with title and bullet points";

const Schema = z.object({
  title: z.string().default('Slide Title'),
  content: z.array(z.string()).default(['Point 1', 'Point 2', 'Point 3']).describe('Bullet points'),
  show_logo: z.boolean().default(true).describe('Show USDAW logo in header')
});

const dynamicSlideLayout = ({ data }) => {
  const { title = 'Slide Title', content = [], show_logo = true } = data || {};

  const containerStyle = {
    width: '100%',
    height: '100vh',
    backgroundColor: '#FFFFFF',
    display: 'flex',
    flexDirection: 'column',
    padding: 0,
    boxSizing: 'border-box'
  };

  const headerStyle = {
    backgroundColor: '#8F1A95',
    padding: '20px 40px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const titleStyle = {
    fontSize: '32px',
    fontFamily: 'Calibri Light, sans-serif',
    fontWeight: '300',
    color: '#FFFFFF',
    margin: 0
  };

  const logoStyle = {
    height: '35px'
  };

  const contentStyle = {
    flex: 1,
    padding: '40px 60px',
    overflow: 'hidden'
  };

  const listStyle = {
    fontSize: '24px',
    fontFamily: 'Calibri, sans-serif',
    color: '#333333',
    lineHeight: '1.8',
    margin: 0,
    paddingLeft: '30px'
  };

  const listItemStyle = {
    marginBottom: '15px'
  };

  return (
    <div style={containerStyle} data-layout="title-and-content">
      <div style={headerStyle}>
        <h1 style={titleStyle}>{title}</h1>
        {show_logo && (
          <img 
            src="/images/usdaw-template-new/usdaw-logo-white.svg" 
            alt="USDAW" 
            style={logoStyle}
          />
        )}
      </div>
      <div style={contentStyle}>
        <ul style={listStyle}>
          {content.map((item, idx) => (
            <li key={idx} style={listItemStyle}>{item}</li>
          ))}
        </ul>
      </div>
    </div>
  );
};

