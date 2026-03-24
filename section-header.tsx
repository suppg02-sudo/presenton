const layoutId = "section-header";
const layoutName = "Section Header";
const layoutDescription = "A section divider slide with title and subtitle on USDAW purple background";

const Schema = z.object({
  title: z.string().default('Section Title'),
  subtitle: z.string().default('Subtitle')
});

const dynamicSlideLayout = ({ data }) => {
  const {
    title = 'Section Title',
    subtitle = 'Subtitle'
  } = data || {};

  return (
    <div style={{
      width: '100%',
      height: '100vh',
      backgroundColor: '#8F1A95',
      display: 'flex',
      flexDirection: 'column',
      justifyContent: 'center',
      alignItems: 'center',
      padding: '40px',
      margin: '0',
      boxSizing: 'border-box'
    }} data-layout="section-header">
      <div style={{
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
        alignItems: 'center',
        width: '100%',
        textAlign: 'center'
      }}>
        <h1 style={{
          fontSize: '72px',
          fontFamily: 'Calibri Light, Calibri, sans-serif',
          color: '#FFFFFF',
          fontWeight: '300',
          margin: '0 0 20px 0',
          lineHeight: '1.2'
        }}>
          {title}
        </h1>
        {subtitle && (
          <p style={{
            fontSize: '32px',
            fontFamily: 'Calibri, sans-serif',
            color: '#FFFFFF',
            fontWeight: '400',
            margin: '0',
            lineHeight: '1.4'
          }}>
            {subtitle}
          </p>
        )}
      </div>
    </div>
  );
};
